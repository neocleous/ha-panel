#!/usr/bin/env python3
"""
HA Panel — screen sleep + auto-brightness daemon.

Sleep: turns the backlight off after a period of touch inactivity and wakes
it on the next touch. While the screen is asleep the touchscreen is held
under an exclusive evdev grab (EVIOCGRAB), so the wake touch — and the whole
gesture it belongs to — is swallowed and never reaches the compositor or
Chromium. No accidental button presses when waking the panel.

Auto-brightness: while awake, the backlight level follows ambient light.
The lux value comes from the sensor daemon via the MQTT broker (retained
topic <MQTT_TOPIC_ROOT>/sensor/light) — no second I2C reader on the
VEML6030, and the values match sensor.panel_XX_light in HA exactly, so the
anchors can be tuned against what HA shows. If MQTT or the config are
unavailable, brightness stays fixed at --on; if lux merely goes stale, the
last level is held (no jumps).

Mapping: log(lux) → linear brightness between two anchors (perceived
brightness is logarithmic). Tunables live in /opt/ha-panel/sensor-config.py;
all are optional, defaults in brackets:

    AUTO_BRIGHTNESS = True     # [True]  False = fixed --on brightness
    BRIGHTNESS_MIN  = 15       # [15]    level at/below LUX_DARK
    BRIGHTNESS_MAX  = 255      # [255]   level at/above LUX_BRIGHT
    LUX_DARK        = 2.0      # [2.0]   lux reading when the room feels dark
    LUX_BRIGHT      = 150.0    # [150.0] lux reading in bright daylight —
                               # the sensor sits at the column base and
                               # under-reads vs the screen face; tune against
                               # sensor.panel_XX_light, not a lux app

Replaces swayidle: do not run both.

Requirements:
  - evdev + paho-mqtt: run with /opt/ha-panel/venv/bin/python3 — the venv is
    created with --system-site-packages, so apt's python3-evdev is visible
    inside it alongside pip's paho-mqtt. Under system python3 (no paho) the
    daemon still runs, with auto-brightness disabled.
  - user in 'input' group (read/grab /dev/input/event*)
  - write access to the backlight brightness node (udev rule: video group g+w)

Usage (from labwc autostart):
  /opt/ha-panel/venv/bin/python3 screen-sleep.py --timeout 10 \
      --backlight /sys/class/backlight/11-0045/brightness --on 200 \
      --config /opt/ha-panel/sensor-config.py
"""

import argparse
import importlib.util
import math
import select
import sys
import threading
import time

from evdev import InputDevice, ecodes, list_devices

# Minimum change (0–255 scale) before a new brightness level is written —
# stops the backlight visibly hunting on small lux fluctuations.
BRIGHTNESS_DEADBAND = 6


def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} screen-sleep: {msg}", flush=True)


def find_touchscreen():
    """Return the first evdev device with multitouch absolute axes."""
    for path in list_devices():
        try:
            dev = InputDevice(path)
        except OSError:
            continue
        caps = dev.capabilities()
        abs_caps = caps.get(ecodes.EV_ABS, [])
        abs_codes = [code for code, _ in abs_caps]
        if ecodes.ABS_MT_POSITION_X in abs_codes:
            return dev
        dev.close()
    return None


def set_backlight(path, value):
    try:
        with open(path, "w") as f:
            f.write(str(value))
    except OSError as e:
        log(f"backlight write failed: {e}")


def drain(dev):
    """Read and discard all pending events."""
    try:
        while dev.read_one() is not None:
            pass
    except BlockingIOError:
        pass


def load_config(path):
    """Import the panel sensor config as a module. None on any failure."""
    try:
        spec = importlib.util.spec_from_file_location("panel_sensor_config", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        log(f"config load failed ({path}): {e} — auto-brightness disabled")
        return None


class AmbientLight:
    """Latest lux from the sensor daemon via MQTT (retained topic).

    .enabled is True only when the MQTT subscription was set up; .read()
    returns the latest lux or None if nothing has been received yet.
    """

    def __init__(self, cfg):
        self.enabled = False
        self._lux = None
        self._lock = threading.Lock()

        if cfg is None:
            return
        if not getattr(cfg, "AUTO_BRIGHTNESS", True):
            log("auto-brightness disabled in config")
            return
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            log("paho-mqtt not importable — auto-brightness disabled "
                "(run with /opt/ha-panel/venv/bin/python3)")
            return
        try:
            panel_id = cfg.PANEL_ID
            broker = cfg.MQTT_BROKER
            user = cfg.MQTT_USERNAME
            password = cfg.MQTT_PASSWORD
        except AttributeError as e:
            log(f"config missing MQTT settings ({e}) — auto-brightness disabled")
            return
        port = int(getattr(cfg, "MQTT_PORT", 1883))
        topic_root = getattr(cfg, "MQTT_TOPIC_ROOT", f"home/{panel_id}")
        topic = f"{topic_root}/sensor/light"

        # client_id MUST differ from the sensor daemon's (which uses PANEL_ID)
        # — identical ids make the broker disconnect the other client in a loop.
        client_id = f"{panel_id}-screensleep"
        try:
            client = mqtt.Client(
                client_id=client_id,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            )
        except (AttributeError, TypeError):
            client = mqtt.Client(client_id=client_id)  # paho 1.x
        client.username_pw_set(user, password)

        def on_connect(c, userdata, flags, rc, *args):
            if rc == 0:
                c.subscribe(topic)
                log(f"mqtt connected, subscribed {topic}")
            else:
                log(f"mqtt connect failed rc={rc}")

        def on_message(c, userdata, msg):
            try:
                value = float(msg.payload.decode())
            except (ValueError, UnicodeDecodeError):
                return
            with self._lock:
                self._lux = value

        client.on_connect = on_connect
        client.on_message = on_message
        client.reconnect_delay_set(min_delay=1, max_delay=60)
        try:
            # connect_async + loop_start: never blocks startup, reconnects
            # forever in the background if the broker is unreachable.
            client.connect_async(broker, port, keepalive=60)
            client.loop_start()
        except Exception as e:
            log(f"mqtt setup failed: {e} — auto-brightness disabled")
            return
        self.enabled = True
        log(f"auto-brightness: lux from {broker}:{port} {topic}")

    def read(self):
        with self._lock:
            return self._lux


def make_brightness_fn(cfg, ambient, fallback):
    """Return a zero-arg function giving the current target brightness."""
    bmin = int(getattr(cfg, "BRIGHTNESS_MIN", 15)) if cfg else fallback
    bmax = int(getattr(cfg, "BRIGHTNESS_MAX", 255)) if cfg else fallback
    ldark = float(getattr(cfg, "LUX_DARK", 2.0)) if cfg else 2.0
    lbright = float(getattr(cfg, "LUX_BRIGHT", 150.0)) if cfg else 150.0
    if ldark <= 0:
        ldark = 0.1
    if lbright <= ldark:
        lbright = ldark * 10
    log_span = math.log(lbright) - math.log(ldark)

    def target():
        if not ambient.enabled:
            return fallback
        lux = ambient.read()
        if lux is None:          # nothing received yet
            return fallback
        if lux <= ldark:
            return bmin
        if lux >= lbright:
            return bmax
        f = (math.log(lux) - math.log(ldark)) / log_span
        return round(bmin + f * (bmax - bmin))

    return target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=10.0,
                    help="seconds of inactivity before screen off")
    ap.add_argument("--backlight", default="/sys/class/backlight/11-0045/brightness")
    ap.add_argument("--on", type=int, default=200,
                    help="brightness when awake (fallback when no lux available)")
    ap.add_argument("--off", type=int, default=0, help="brightness when asleep")
    ap.add_argument("--config", default="/opt/ha-panel/sensor-config.py",
                    help="panel sensor config (MQTT + brightness tunables)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    ambient = AmbientLight(cfg)
    target_brightness = make_brightness_fn(cfg, ambient, args.on)

    dev = None
    while dev is None:
        dev = find_touchscreen()
        if dev is None:
            log("no touchscreen found — retrying in 5s")
            time.sleep(5)

    log(f"touchscreen: {dev.name} ({dev.path}), timeout {args.timeout}s")

    current = target_brightness()
    set_backlight(args.backlight, current)
    awake = True
    last_input = time.monotonic()

    while True:
        try:
            r, _, _ = select.select([dev.fd], [], [], 0.5)

            if r:
                if awake:
                    # Normal activity — consume events, reset idle timer
                    drain(dev)
                    last_input = time.monotonic()
                else:
                    # Wake touch while grabbed: turn screen on, then swallow
                    # the entire gesture (keep grabbed until 300ms of silence
                    # after the finger lifts).
                    current = target_brightness()
                    set_backlight(args.backlight, current)
                    drain(dev)
                    while True:
                        r2, _, _ = select.select([dev.fd], [], [], 0.3)
                        if not r2:
                            break
                        drain(dev)
                    try:
                        dev.ungrab()
                    except OSError:
                        pass
                    awake = True
                    last_input = time.monotonic()
                    log(f"woke on touch (gesture swallowed, brightness {current})")

            if awake:
                # Ambient tracking — deadbanded so small lux wobble is ignored
                t = target_brightness()
                if abs(t - current) >= BRIGHTNESS_DEADBAND:
                    set_backlight(args.backlight, t)
                    current = t
                    log(f"brightness -> {t} (lux {ambient.read()})")

                if (time.monotonic() - last_input) > args.timeout:
                    try:
                        dev.grab()
                    except OSError as e:
                        log(f"grab failed: {e}")
                    set_backlight(args.backlight, args.off)
                    awake = False
                    log("screen off (touch grabbed)")

        except OSError as e:
            # Device vanished (e.g. driver reload) — reacquire
            log(f"device error: {e} — reacquiring")
            try:
                dev.close()
            except Exception:
                pass
            dev = None
            current = target_brightness()
            set_backlight(args.backlight, current)
            awake = True
            while dev is None:
                time.sleep(3)
                dev = find_touchscreen()
            last_input = time.monotonic()
            log(f"reacquired: {dev.path}")


if __name__ == "__main__":
    sys.exit(main())

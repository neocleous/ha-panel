#!/usr/bin/env python3
"""
HA Panel — screen sleep daemon.

Turns the backlight off after a period of touch inactivity and wakes it on
the next touch. While the screen is asleep the touchscreen is held under an
exclusive evdev grab (EVIOCGRAB), so the wake touch — and the whole gesture
it belongs to — is swallowed and never reaches the compositor or Chromium.
No accidental button presses when waking the panel.

Replaces swayidle: do not run both.

Requirements:
  - python3-evdev (apt)
  - user in 'input' group (read/grab /dev/input/event*)
  - write access to the backlight brightness node (udev rule: video group g+w)

Usage (from labwc autostart):
  python3 screen-sleep.py --timeout 10 \
      --backlight /sys/class/backlight/11-0045/brightness --on 200
"""

import argparse
import select
import sys
import time

from evdev import InputDevice, ecodes, list_devices


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=10.0,
                    help="seconds of inactivity before screen off")
    ap.add_argument("--backlight", default="/sys/class/backlight/11-0045/brightness")
    ap.add_argument("--on", type=int, default=200, help="brightness when awake")
    ap.add_argument("--off", type=int, default=0, help="brightness when asleep")
    args = ap.parse_args()

    dev = None
    while dev is None:
        dev = find_touchscreen()
        if dev is None:
            log("no touchscreen found — retrying in 5s")
            time.sleep(5)

    log(f"touchscreen: {dev.name} ({dev.path}), timeout {args.timeout}s")

    set_backlight(args.backlight, args.on)
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
                    set_backlight(args.backlight, args.on)
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
                    log("woke on touch (gesture swallowed)")

            if awake and (time.monotonic() - last_input) > args.timeout:
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
            set_backlight(args.backlight, args.on)
            awake = True
            while dev is None:
                time.sleep(3)
                dev = find_touchscreen()
            last_input = time.monotonic()
            log(f"reacquired: {dev.path}")


if __name__ == "__main__":
    sys.exit(main())

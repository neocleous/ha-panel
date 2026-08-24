# Home Assistant Touch Panel

A desk-mounted Home Assistant touch panel, vibe coded from start to finish — the software in this repo was written end-to-end by an AI assistant (Claude) in conversation with the maintainer, hardware debugging included. Read it with that in mind; it runs a real panel every day, but nobody hand-crafted it.

Built on a Raspberry Pi 5 with a Waveshare 8" DSI touchscreen, environmental sensors, capacitive touch buttons, and a 3D-printable desk-stand enclosure ([STEP file](https://github.com/neocleous/ha-panel/blob/docs/enclosure/HA%20Panel%20Final.step) on the `docs` branch). Home Assistant runs on a separate server — each panel is a pure display and sensor client, no HAOS on the panel itself.

## What it does

- **Kiosk dashboard** — Chromium in app mode under labwc (Wayland), portrait, no window chrome, with a working on-screen keyboard (squeekboard)
- **Screen sleep** — backlight off after touch inactivity; the wake tap is swallowed via an evdev grab so it never presses anything in the UI
- **Auto-brightness** — backlight follows ambient light from the VEML6030, delivered over MQTT
- **Dark mode** — follows sunset/sunrise via a retained MQTT topic published by an HA automation; Chromium restarts with `--force-dark-mode`
- **Environmental sensors** — temperature, humidity, pressure, VOC (BME680) and ambient light, auto-registered in HA via MQTT discovery
- **Physical buttons** — four capacitive touch buttons (AT42QT1070 on a custom PCB) that work even with the screen asleep
- **Self-updating** — nightly systemd timer runs a full unattended OS + firmware + repo update, showing a progress splash if anyone touches the screen mid-update
- **Zero-touch provisioning** — the [Panel Setup](tools/panel-setup/) app writes first-boot files to a freshly flashed SD card; the panel installs itself and boots into the dashboard in ~10 minutes

## Hardware

| Component | Part |
|-----------|------|
| Compute | Raspberry Pi 5 (4 GB) |
| Display | Waveshare 8inch DSI LCD (C), 1280×800 IPS, portrait |
| Touch buttons | AT42QT1070 on a custom PCB (I2C 0x1B, 4 capacitive electrodes) |
| Temp / humidity / pressure / VOC | BME680 breakout (I2C 0x77) |
| Ambient light | VEML6030 breakout (I2C 0x48) |
| Proximity | VL53L0X breakout (I2C 0x29) |
| Power | USB-C (Adafruit USB Type C vertical breakout) |
| Enclosure | 3D-printed desk stand — STEP on the `docs` branch |

All sensors sit on the Pi's I2C bus 1. The sensor cluster lives at the base of the stand, ventilated top-to-bottom, away from display/Pi heat.

## Deploying a panel

The easy way — **[Panel Setup](tools/panel-setup/)** (macOS / Windows / Linux, single binary, no dependencies):

1. Flash Raspberry Pi OS Lite (64-bit) with Raspberry Pi Imager — **no** Imager customisation
2. Run Panel Setup, fill the form (it tests your MQTT credentials against the broker before letting you write)
3. It writes `userconf.txt` + `firstrun.sh` to the SD card
4. Insert, power on, wait ~10 minutes — the panel installs everything and boots into your dashboard

Binaries on the [Releases page](../../releases); build details and the unsigned-app first-run notes are in [tools/panel-setup/README.md](tools/panel-setup/README.md).

The manual way — SSH install with `system/install.sh` — is documented in [system/README.md](system/README.md).

## Repository layout

```
ha-panel/
├── sensor-daemon/        # MQTT discovery + I2C polling (systemd service)
│   └── sensors/          # AT42QT1070, BME680, VL53L0X, VEML6030 drivers
├── system/               # Kiosk stack: startup.sh, screen-sleep.py,
│                         # nightly update.sh + timer, update splash
├── provisioning-ui/      # On-device touchscreen setup wizard
└── tools/panel-setup/    # Cross-platform SD-card preparation app (Go)
```

Per-panel state lives outside the repo on the device (`/opt/ha-panel/config` and `/opt/ha-panel/sensor-config.py`) and survives the nightly `git reset --hard`. **Never commit credentials to this repo.**

## How the kiosk works

```
TTY1 autologin (.bash_profile)
  └── startup.sh
        ├── sources /opt/ha-panel/config
        ├── writes labwc rc.xml   (touch→output mapping, undecorated maximised windows)
        ├── writes labwc autostart (screen-sleep, squeekboard, chromium loop)
        └── exec labwc
              ├── screen-sleep.py  (sleep/wake + auto-brightness + theme switch)
              ├── squeekboard      (on-screen keyboard)
              └── chromium --app=<HA dashboard>  (restarts on crash/theme/update)
```

MQTT topics follow `home/<panel-id>/…`; the fleet-wide dark-mode topic is `home/panels/theme`.

## SSH access

Panels accept SSH from the local /24 only (nftables). `ssh you@panel-01.local`.

## Troubleshooting

First stops: `/var/log/ha-panel-startup.log` on the panel, `journalctl -u sensor-daemon`, `/var/log/ha-panel-update.log` for the nightly update, and `firstrun.log` on the SD card's boot partition if first boot fails. More in [system/README.md](system/README.md).

## License

[PolyForm Noncommercial 1.0.0](LICENSE.md) — free for personal, hobby, educational, and other noncommercial use: build panels, modify the code, share it. **Commercial use is not permitted.** If you want to use this commercially, contact the maintainer about a separate license.

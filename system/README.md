# HA Panel

Wall-mounted Home Assistant touch panel built on Raspberry Pi 5 with a Waveshare 8" DSI display.

HA runs on a separate server. Each panel is a pure display and sensor client — no HAOS on the panel itself.

---

## Hardware

| Component | Part |
|-----------|------|
| Compute | Raspberry Pi 5 (4GB) |
| Display | Waveshare 8inch DSI LCD (C), 1280×800 IPS |
| Touch controller | AT42QT1070 (custom PCB, I2C, 4 buttons) |
| Temp / humidity / pressure / VOC | BME680 breakout (I2C 0x76) |
| Proximity (screen wake) | VL53L0X breakout (I2C 0x29) |
| Ambient light | VEML6030 breakout (I2C 0x10) |
| Power | USB-C (custom power board) |

All sensors connect directly to the Pi's I2C bus 1. No sensors are on the touch PCB.

---

## Repository layout

```
ha-panel/
├── sensor-daemon/
│   ├── main.py              # MQTT discovery + I2C polling loop
│   ├── config.py            # All configurable values
│   ├── backlight.py         # sysfs backlight control
│   ├── requirements.txt
│   └── sensors/
│       ├── at42qt1070.py    # Touch buttons (KEY0–KEY3)
│       ├── bme680.py        # Temp / humidity / pressure / VOC
│       ├── vl53l0x.py       # Proximity (ToF)
│       └── veml6030.py      # Ambient light
├── provisioning-ui/
│   ├── index.html           # Wi-Fi network list
│   ├── password.html        # Password entry + on-screen keyboard
│   └── server.py            # Local HTTP server (port 8080)
└── system/
    ├── install.sh           # Full install script for a new panel
    ├── startup.sh           # Kiosk startup: writes labwc config, launches labwc
    ├── update.sh            # Nightly update script
    ├── panel-update.timer   # systemd timer (2am)
    ├── panel-update.service
    └── sensor-daemon.service
```

---

## Deploying a new panel

### Step 1 — Flash SD card

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) with these settings:

| Setting | Value |
|---------|-------|
| OS | Raspberry Pi OS Lite (64-bit) |
| Hostname | `panel-02` (increment for each panel) |
| Username | `pi` |
| Password | *(your chosen password)* |
| SSH | Enable — password authentication |
| Wi-Fi | Configure your network |
| Locale | Set your timezone and keyboard layout |

### Step 2 — Boot and SSH in

Insert the SD card, connect the DSI display, and power on. Wait ~60 seconds for first boot, then SSH in:

```bash
ssh pi@panel-02.local
# or use the IP address if mDNS isn't available
```

### Step 3 — Run the install script

You need a GitHub Personal Access Token (PAT) with `repo` read scope to download the script from the private repo. Create one at: https://github.com/settings/tokens

Then run:

```bash
curl -fsSL \
  -H "Authorization: token YOUR_GITHUB_PAT" \
  "https://raw.githubusercontent.com/neocleous/ha-panel/main/system/install.sh" \
  | sudo bash
```

The script will:

1. Install all required packages
2. Configure the display overlay, I2C, Bluetooth disable, and autologin
3. Generate a unique SSH deploy key for this panel
4. **Pause and show you the public key** — add it to GitHub before continuing
5. Clone the repo to `/opt/ha-panel/repo`
6. Set up the Python venv and install sensor daemon dependencies
7. Enable the sensor daemon and nightly update timer
8. Configure the firewall
9. Offer to reboot

### Step 4 — Add the deploy key to GitHub

When the script pauses, it will display the public key and instructions. Go to:

**https://github.com/neocleous/ha-panel/settings/keys → Add deploy key**

- Title: the panel ID (e.g. `panel-02`)
- Key: paste the public key shown by the script
- Allow write access: **leave unchecked**

Press Enter in the terminal to continue.

### Step 5 — Reboot

The script will offer to reboot. After reboot the panel will automatically:

- Log in as `pi` on TTY1
- Launch labwc (Wayland compositor)
- Start Chromium in app mode pointing at HA
- Register all sensors with HA via MQTT discovery

---

## How it works

### Display stack

```
TTY1 autologin (.bash_profile)
  └── startup.sh
        ├── Writes ~/.config/labwc/rc.xml  (touch mapping, window rules)
        ├── Writes ~/.config/labwc/autostart  (squeekboard + chromium loop)
        └── Launches labwc
              ├── squeekboard  (on-screen keyboard)
              └── chromium --app=http://HA_URL (kiosk, maximised, no decorations)
```

### Sensor daemon

Runs as a system service (`sensor-daemon.service`). On startup it publishes MQTT discovery messages so all entities appear automatically in HA under the panel's device. It then polls sensors every ~5 seconds and publishes readings.

Entities registered per panel:

| Entity | Type |
|--------|------|
| Temperature | Sensor |
| Humidity | Sensor |
| Pressure | Sensor |
| VOC | Sensor |
| Light | Sensor |
| Proximity | Sensor |
| Button 0–3 | Binary sensor |
| Backlight | Switch |

MQTT topics follow the pattern: `home/{panel-id}/sensor/*`

### Nightly updates

A systemd timer fires at 2:00–2:05am (random stagger between panels). The update script:

1. Turns the screen off
2. Runs `apt upgrade`
3. Updates `rpi-eeprom`
4. Upgrades Python packages in the venv
5. Pulls the latest repo via `git reset --hard origin/main`
6. Reboots if the kernel, eeprom, or repo changed

### Wi-Fi provisioning

If the panel boots without a network connection, `startup.sh` starts the provisioning server on port 8080 and loads `http://localhost:8080` in Chromium instead of HA. The provisioning UI shows available networks and a touch keyboard for password entry.

---

## Configuration

All configurable values are in `sensor-daemon/config.py`:

```python
PANEL_ID = "panel-01"       # Must match hostname
HA_URL   = "http://192.168.1.145:8123"
MQTT_HOST = "192.168.1.145"
MQTT_PORT = 1883
MQTT_USER = "ha-panel"
MQTT_PASS = "your-password"
```

The HA URL and MQTT settings are also hardcoded in `system/startup.sh` and `system/install.sh`. If you change your HA server address, update all three files.

---

## Troubleshooting

### Touchscreen not working after reboot

The touchscreen requires labwc to be started from a proper login session (not a systemd service). Confirm autologin is active:

```bash
sudo raspi-config nonint get_autologin
# Should return: 1
```

Check the labwc process is running and was started from bash (not systemd):

```bash
ps -o pid,ppid,cmd $(pgrep labwc)
# PPID should be a bash shell, not systemd (PID 1)
```

### On-screen keyboard not appearing

Squeekboard only appears above maximised windows, not true fullscreen. Chromium must be launched with `--app=URL --start-maximized` (not `--kiosk`). Confirm:

```bash
pgrep -a chromium | grep "app="
```

### Sensor daemon not connecting to MQTT

Check the service logs:

```bash
sudo journalctl -u sensor-daemon --no-pager | tail -30
```

Verify the MQTT credentials in `sensor-daemon/config.py` match those in your HA MQTT integration.

### Backlight not controlled

Find the correct sysfs path:

```bash
ls /sys/class/backlight/
```

Update `BACKLIGHT_PATH` in `system/startup.sh` to match.

### Display not turning on

Verify the correct overlay is set in `/boot/firmware/config.txt`:

```
dtoverlay=vc4-kms-dsi-waveshare-panel,8_0_inch
```

---

## SSH access

Each panel accepts SSH from the local network only (firewall rule: `192.168.1.0/24`).

```bash
ssh pi@panel-01.local
ssh pi@panel-02.local
```

Cockpit web console is available at `https://panel-01.local:9090`

---

## Adding a second panel to HA

No manual HA configuration is needed. When the sensor daemon starts on a new panel it publishes MQTT discovery messages automatically. The new panel will appear in:

**HA → Settings → Devices & Services → MQTT → Devices**

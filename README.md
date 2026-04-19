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
| Power | USB-C (Adafruit USB Type C Vertical Breakout or custom power board) |

All sensors connect directly to the Pi's I2C bus 1. No sensors are on the touch PCB.

---

## Repository layout

```
ha-panel/
├── sensor-daemon/
│   ├── main.py              # MQTT discovery + I2C polling loop
│   ├── config.py            # Your local config — NOT committed (see .gitignore)
│   ├── config.example.py    # Template — copy to config.py and fill in values
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

## Configuration

Before running the sensor daemon, copy the example config and fill in your values:

```bash
cp /opt/ha-panel/repo/sensor-daemon/config.example.py \
   /opt/ha-panel/repo/sensor-daemon/config.py
nano /opt/ha-panel/repo/sensor-daemon/config.py
```

Set at minimum:
- `PANEL_ID` — must match the hostname (e.g. `panel-01`)
- `MQTT_BROKER` — your HA server IP
- `MQTT_USERNAME` / `MQTT_PASSWORD` — MQTT credentials from HA

The HA dashboard URL is set in `/opt/ha-panel/config`:

```bash
HA_URL=http://YOUR_HA_IP:8123
```

**Never commit `config.py` to the repo.** It is listed in `.gitignore`.

---

## Deploying a new panel

### Step 1 — Flash SD card

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) with these settings:

| Setting | Value |
|---------|-------|
| OS | Raspberry Pi OS Lite (64-bit) |
| Hostname | `panel-01` (increment for each panel) |
| Username | *(your chosen username)* |
| Password | *(your chosen password)* |
| SSH | Enable — password authentication |
| Wi-Fi | Configure your network |
| Locale | Set your timezone and keyboard layout |

### Step 2 — Boot and SSH in

Insert the SD card, connect the DSI display, and power on. Wait ~60 seconds for first boot, then SSH in:

```bash
ssh yourusername@panel-01.local
# or use the IP address if mDNS isn't available
```

### Step 3 — Run the install script

```bash
curl -fsSL https://raw.githubusercontent.com/neocleous/ha-panel/main/system/install.sh \
  -o /tmp/install.sh && sudo bash /tmp/install.sh
```

The script will:

1. Detect your username automatically
2. Install all required packages
3. Configure the display overlay, I2C, Bluetooth disable, and autologin
4. Clone the repo to `/opt/ha-panel/repo`
5. Set up the Python venv
6. Configure the firewall
7. Offer to reboot

### Step 4 — Configure the panel

After the install, copy and edit the sensor daemon config:

```bash
cp /opt/ha-panel/repo/sensor-daemon/config.example.py \
   /opt/ha-panel/repo/sensor-daemon/config.py
nano /opt/ha-panel/repo/sensor-daemon/config.py
```

Then create the panel config file:

```bash
sudo nano /opt/ha-panel/config
```

Add:

```
HA_URL=http://YOUR_HA_IP:8123
```

Then reboot. The panel will start automatically.

---

## How it works

### Display stack

```
TTY1 autologin (.bash_profile)
  └── startup.sh
        ├── Sources /opt/ha-panel/config
        ├── Writes ~/.config/labwc/rc.xml  (touch mapping, window rules)
        ├── Writes ~/.config/labwc/autostart  (squeekboard + chromium loop)
        └── Launches labwc
              ├── squeekboard  (on-screen keyboard)
              └── chromium --app=HA_URL (kiosk, maximised, no decorations)
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

A systemd timer fires at 2:00–2:05am. The update script:

1. Turns the screen off
2. Runs `apt upgrade`
3. Updates `rpi-eeprom`
4. Upgrades Python packages in the venv
5. Pulls the latest repo via `git reset --hard origin/main`
6. Reboots if the kernel or eeprom changed

### Wi-Fi provisioning

If the panel boots without a network connection, `startup.sh` starts the provisioning server on port 8080 and loads `http://localhost:8080` in Chromium instead of HA.

---

## SSH access

Each panel accepts SSH from the local network only (firewall rule: `192.168.1.0/24`).

```bash
ssh yourusername@panel-01.local
ssh yourusername@panel-02.local
```

---

## Adding a second panel to HA

No manual HA configuration is needed. When the sensor daemon starts on a new panel it publishes MQTT discovery messages automatically. The new panel will appear in:

**HA → Settings → Devices & Services → MQTT → Devices**

---

## Troubleshooting

### Touchscreen not working after reboot

Confirm autologin is active:

```bash
sudo raspi-config nonint get_autologin
# Should return: 1
```

### On-screen keyboard not appearing

Chromium must be launched with `--app=URL --start-maximized` (not `--kiosk`). Confirm:

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

Update `BACKLIGHT_PATH` in `sensor-daemon/config.py` to match.

### Display not turning on

Verify the correct overlay is set in `/boot/firmware/config.txt`:

```
dtoverlay=vc4-kms-dsi-waveshare-panel,8_0_inch
```

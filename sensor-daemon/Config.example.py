# ─────────────────────────────────────────────────────────────────────────────
# HA Panel — Sensor Daemon Configuration Example
# Copy this file to config.py and fill in your values.
# config.py is listed in .gitignore and will never be committed to the repo.
# ─────────────────────────────────────────────────────────────────────────────

# Panel identity — must match the hostname set during imaging (e.g. panel-01)
PANEL_ID = "panel-01"

# Home Assistant MQTT broker
MQTT_BROKER = "192.168.1.x"        # Your HA server IP
MQTT_PORT = 1883
MQTT_USERNAME = "ha-panel"         # MQTT username configured in HA
MQTT_PASSWORD = ""                 # MQTT password configured in HA

# MQTT topic root — do not change
MQTT_TOPIC_ROOT = f"home/{PANEL_ID}"

# I2C bus number on Pi 5
I2C_BUS = 1

# Polling intervals in seconds
POLL_INTERVAL_TOUCH = 0.1       # AT42QT1070 — 100ms
POLL_INTERVAL_PROXIMITY = 0.2   # VL53L0X — 200ms
POLL_INTERVAL_LIGHT = 10        # VEML6030 — 10s
POLL_INTERVAL_ENV = 30          # BME680 — 30s

# Screen wake proximity threshold in mm
PROXIMITY_WAKE_THRESHOLD_MM = 120   # 12cm

# Backlight sysfs path
BACKLIGHT_PATH = "/sys/class/backlight/11-0045/brightness"
BACKLIGHT_MAX = 255
BACKLIGHT_ON = 255
BACKLIGHT_OFF = 0

# Screen wake timeout in seconds — screen turns off after this
# if no proximity detected
SCREEN_TIMEOUT = 60

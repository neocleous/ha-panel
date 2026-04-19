#!/bin/bash

CONFIG_FILE="/opt/ha-panel/config"
BACKLIGHT_PATH="/sys/class/backlight/11-0045/brightness"
LOG_FILE="/var/log/ha-panel-startup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE" 2>/dev/null || true
}

log "=== Startup ==="

# Load config if it exists
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck source=/dev/null
    source "$CONFIG_FILE"
else
    log "WARNING: No config file found at $CONFIG_FILE — provisioning mode"
fi

# Use backlight path from config if set, otherwise use default
BACKLIGHT="${BACKLIGHT_PATH_OVERRIDE:-$BACKLIGHT_PATH}"
echo 255 > "$BACKLIGHT" 2>/dev/null || true

# Wait for network
ATTEMPTS=0
while [ $ATTEMPTS -lt 30 ]; do
    STATE=$(nmcli -t -f STATE general 2>/dev/null)
    if echo "$STATE" | grep -q "connected"; then
        log "Network connected"
        break
    fi
    ATTEMPTS=$((ATTEMPTS + 1))
    sleep 2
done

if [ $ATTEMPTS -eq 30 ]; then
    log "No network — starting provisioning"
    systemctl --user start provisioning-server.service
    sleep 2
    DISPLAY_URL="http://localhost:8080"
elif [ -z "$HA_URL" ]; then
    log "No HA_URL in config — starting provisioning"
    systemctl --user start provisioning-server.service
    sleep 2
    DISPLAY_URL="http://localhost:8080"
else
    DISPLAY_URL="$HA_URL"
fi

log "Writing labwc config"

mkdir -p ~/.config/labwc

cat > ~/.config/labwc/autostart << EOAUTO
squeekboard &
while true; do sleep 3600; done &
while true; do
    /usr/lib/chromium/chromium --app=$DISPLAY_URL --start-maximized --no-first-run --disable-infobars --disable-translate --disable-features=TranslateUI --disable-sync --disable-background-networking --disable-default-apps --no-default-browser-check --disable-session-crashed-bubble --disable-component-update --ozone-platform=wayland --disable-gpu-vsync --enable-wayland-ime
    sleep 2
done &
EOAUTO

cat > ~/.config/labwc/rc.xml << 'EORC'
<?xml version="1.0"?>
<labwc_config>
  <core>
    <decoration>client</decoration>
  </core>
  <theme>
    <maximizedDecoration>none</maximizedDecoration>
  </theme>
  <touch>
    <deviceName>11-0014 Goodix Capacitive TouchScreen</deviceName>
    <mapToOutput>DSI-2</mapToOutput>
    <mouseEmulation>no</mouseEmulation>
  </touch>
  <windowRules>
    <windowRule identifier="chromium" matchType="contains">
      <action name="Maximize"/>
    </windowRule>
  </windowRules>
</labwc_config>
EORC

log "Launching labwc"
labwc

log "labwc exited — restarting"
exec "$0"

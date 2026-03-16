#!/bin/bash

HA_URL="http://192.168.1.145:8123"
BACKLIGHT_PATH="/sys/class/backlight/10-0045/brightness"
LOG_FILE="/var/log/ha-panel-startup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE" 2>/dev/null || true
}

log "=== Startup ==="

echo 255 > "$BACKLIGHT_PATH" 2>/dev/null || true

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
else
    DISPLAY_URL="$HA_URL"
fi

log "Writing wayfire config"

mkdir -p ~/.config
cat > ~/.config/wayfire.ini << WFEOF
[core]
plugins = autostart

[output:DSI-2]
mode = 1280x800@60000
position = 0,0
transform = normal

[input-device:/dev/input/event1]
output = DSI-2

[autostart]
squeekboard = squeekboard
chromium = chromium --kiosk --no-first-run --disable-infobars --disable-translate --disable-features=TranslateUI --disable-sync --disable-background-networking --disable-default-apps --no-default-browser-check --incognito --disable-session-crashed-bubble --disable-component-update $DISPLAY_URL
WFEOF

log "Launching wayfire"
wayfire

log "Wayfire exited — restarting"
exec "$0"

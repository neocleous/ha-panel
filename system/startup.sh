#!/bin/bash

PROVISIONING_DIR="/opt/ha-panel/repo/provisioning-ui"
HA_URL="http://192.168.1.145:8123"
BACKLIGHT_PATH="/sys/class/backlight/10-0045/brightness"
LOG_FILE="/var/log/ha-panel-startup.log"
VENV_PYTHON="/opt/ha-panel/venv/bin/python"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "=== Startup ==="

# Turn screen on
echo 255 > "$BACKLIGHT_PATH" 2>/dev/null

# Wait for networking to be available
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
    log "No network after 60 seconds — starting provisioning"
    START_PROVISIONING=true
else
    # Check HA server is reachable
    if curl -s --connect-timeout 5 "$HA_URL" > /dev/null 2>&1; then
        log "HA server reachable — starting dashboard"
        START_PROVISIONING=false
    else
        log "HA server not reachable — starting dashboard anyway"
        START_PROVISIONING=false
    fi
fi

if [ "$START_PROVISIONING" = true ]; then
    log "Starting provisioning server"
    systemctl start provisioning-server.service
    sleep 2
    DISPLAY_URL="http://localhost:8080"
else
    DISPLAY_URL="$HA_URL"
fi

log "Launching Chromium with URL: $DISPLAY_URL"

# Launch cage with Chromium
cage -- chromium-browser \
    --kiosk \
    --no-first-run \
    --disable-infobars \
    --disable-translate \
    --disable-features=TranslateUI \
    --disable-sync \
    --disable-background-networking \
    --disable-default-apps \
    --no-default-browser-check \
    --incognito \
    --disable-session-crashed-bubble \
    --disable-component-update \
    "$DISPLAY_URL"

log "Chromium exited — restarting startup"
exec "$0"

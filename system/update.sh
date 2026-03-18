#!/bin/bash
LOG_FILE="/var/log/ha-panel-update.log"
REPO_DIR="/opt/ha-panel/repo"
VENV_PIP="/opt/ha-panel/venv/bin/pip"
BACKLIGHT_PATH="/sys/class/backlight/10-0045/brightness"
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}
log "=== Update started ==="
# Turn screen off
echo 0 > "$BACKLIGHT_PATH" 2>/dev/null
# Stop sensor daemon during update
systemctl stop sensor-daemon.service
log "Sensor daemon stopped"
# Step 1 — OS packages
log "Running apt update..."
apt-get update -qq >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: apt update failed — aborting"
    systemctl start sensor-daemon.service
    exit 1
fi
log "Running apt upgrade..."
apt-get upgrade -y -qq >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: apt upgrade failed — aborting"
    systemctl start sensor-daemon.service
    exit 1
fi
apt-get autoremove -y -qq >> "$LOG_FILE" 2>&1
log "apt upgrade complete"
# Step 2 — Pi EEPROM firmware
log "Checking EEPROM firmware..."
EEPROM_OUTPUT=$(rpi-eeprom-update 2>&1)
echo "$EEPROM_OUTPUT" >> "$LOG_FILE"
EEPROM_UPDATED=false
if echo "$EEPROM_OUTPUT" | grep -q "BOOTLOADER: update required"; then
    rpi-eeprom-update -a >> "$LOG_FILE" 2>&1
    EEPROM_UPDATED=true
    log "EEPROM firmware updated"
else
    log "EEPROM firmware is current"
fi
# Step 3 — Python dependencies
log "Upgrading Python dependencies..."
$VENV_PIP install --upgrade -r "$REPO_DIR/sensor-daemon/requirements.txt" -q >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "WARNING: pip upgrade had errors — check log"
else
    log "Python dependencies up to date"
fi
# Step 4 — Pull latest app code from GitHub
log "Pulling latest code from GitHub..."
git -C "$REPO_DIR" pull >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "WARNING: git pull failed — running on previous version"
else
    log "Code pull complete"
fi
chmod +x "$REPO_DIR/system/startup.sh"
chmod +x "$REPO_DIR/system/update.sh"
log "Script permissions set"
# Step 5 — Restart sensor daemon
systemctl start sensor-daemon.service
log "Sensor daemon restarted"
# Step 6 — Reboot if kernel or EEPROM was updated
REBOOT_REQUIRED=false
if [ -f /var/run/reboot-required ]; then
    log "Kernel update detected — reboot required"
    REBOOT_REQUIRED=true
fi
if [ "$EEPROM_UPDATED" = true ]; then
    log "EEPROM update detected — reboot required"
    REBOOT_REQUIRED=true
fi
log "=== Update complete ==="
if [ "$REBOOT_REQUIRED" = true ]; then
    log "Rebooting in 10 seconds..."
    sleep 10
    reboot
fi

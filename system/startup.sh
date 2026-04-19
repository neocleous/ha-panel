#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
#  HA Panel — Kiosk startup script
#  Called from ~/.bash_profile on TTY1 autologin.
#
#  Modes:
#    Provisioning  — /opt/ha-panel/config missing → serve localhost:8080
#    Normal        — config exists → launch HA dashboard in Chromium
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

PANEL_BASE="/opt/ha-panel"
CONFIG_FILE="${PANEL_BASE}/config"
REPO_DIR="${PANEL_BASE}/repo"
PROV_SERVER="${REPO_DIR}/provisioning-ui/server.py"
PROV_URL="http://127.0.0.1:8080"

LABWC_CONFIG_DIR="${HOME}/.config/labwc"

LOG_FILE="/var/log/ha-panel-startup.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "${LOG_FILE}"; }

# ── Wait for display ──────────────────────────────────────────────────────────

log "Startup: waiting for display…"
for i in $(seq 1 30); do
  if [[ -e /dev/dri/card0 ]]; then break; fi
  sleep 1
done

# ── Wait for network (provisioning only needs loopback; normal needs LAN) ─────

wait_for_network() {
  log "Waiting for network connectivity…"
  for i in $(seq 1 30); do
    if nmcli -t -f STATE general 2>/dev/null | grep -q "connected"; then
      log "Network connected."
      return 0
    fi
    sleep 2
  done
  log "Network not available — continuing anyway."
  return 0
}

# ── Backlight ─────────────────────────────────────────────────────────────────

set_backlight() {
  local brightness="${1:-200}"
  # Source config to get the correct backlight path
  local bl_path="/sys/class/backlight/11-0045/brightness"
  if [[ -n "${BACKLIGHT_PATH:-}" ]]; then
    bl_path="${BACKLIGHT_PATH}"
  fi
  if [[ -f "${bl_path}" ]]; then
    echo "${brightness}" > "${bl_path}" 2>/dev/null || true
    log "Backlight set to ${brightness} via ${bl_path}"
  fi
}

# ── labwc config ──────────────────────────────────────────────────────────────

write_labwc_config() {
  local url="$1"
  mkdir -p "${LABWC_CONFIG_DIR}"

  # rc.xml: suppress window decorations, configure touchscreen
  cat > "${LABWC_CONFIG_DIR}/rc.xml" <<XML
<?xml version="1.0" encoding="UTF-8"?>
<labwc_config>
  <core>
    <decoration>client</decoration>
  </core>
  <window>
    <maximizedDecoration>none</maximizedDecoration>
  </window>
  <touch>
    <map from="DSI-1" to="DSI-1"/>
  </touch>
</labwc_config>
XML

  # autostart: squeekboard (OSK) + chromium loop
  cat > "${LABWC_CONFIG_DIR}/autostart" <<SH
# On-screen keyboard
squeekboard &

# Chromium kiosk loop — restarts on crash
while true; do
  chromium-browser \\
    --app="${url}" \\
    --start-maximized \\
    --noerrdialogs \\
    --disable-infobars \\
    --enable-wayland-ime \\
    --ozone-platform=wayland \\
    --no-first-run \\
    --disable-translate \\
    --disable-features=TranslateUI \\
    --check-for-update-interval=31536000
  sleep 3
done &
SH

  log "labwc config written (URL: ${url})"
}

# ── Provisioning mode ─────────────────────────────────────────────────────────

start_provisioning() {
  log "No config found — entering provisioning mode"

  # Check whether we're already connected (ethernet users skip Wi-Fi step)
  # The provisioning UI detects this via /status and routes accordingly.

  # Start the provisioning HTTP server
  if [[ ! -f "${PROV_SERVER}" ]]; then
    log "ERROR: provisioning server not found at ${PROV_SERVER}"
    log "Has the repo been cloned? Run the install script first."
    sleep 30
    return 1
  fi

  python3 "${PROV_SERVER}" >> "${LOG_FILE}" 2>&1 &
  PROV_PID=$!
  log "Provisioning server started (PID ${PROV_PID})"

  # Wait for server to be ready
  for i in $(seq 1 10); do
    if curl -sf "${PROV_URL}" > /dev/null 2>&1; then break; fi
    sleep 0.5
  done

  write_labwc_config "${PROV_URL}"
}

# ── Normal kiosk mode ─────────────────────────────────────────────────────────

start_kiosk() {
  # Source config
  # shellcheck source=/dev/null
  source "${CONFIG_FILE}"

  log "Config loaded: PANEL_ID=${PANEL_ID} HA_URL=${HA_URL}"

  # Set backlight on
  set_backlight 200

  wait_for_network

  write_labwc_config "${HA_URL}"
}

# ── Main ──────────────────────────────────────────────────────────────────────

log "HA Panel startup — PID $$"

if [[ -f "${CONFIG_FILE}" ]]; then
  start_kiosk
else
  start_provisioning
fi

# Launch labwc (blocks until logout/crash)
log "Launching labwc…"
exec labwc

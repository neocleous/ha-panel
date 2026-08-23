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
VENV_PY="${PANEL_BASE}/venv/bin/python3"
SENSOR_CONFIG="${PANEL_BASE}/sensor-config.py"
PROV_SERVER="${REPO_DIR}/provisioning-ui/server.py"
PROV_URL="http://127.0.0.1:8080"

LABWC_CONFIG_DIR="${HOME}/.config/labwc"

# Log to /var/log if writable, otherwise fall back to /tmp.
# (Runs as the panel user — /var/log needs the file pre-created and chowned,
#  which install.sh does; the fallback covers every other case.)
LOG_FILE="/var/log/ha-panel-startup.log"
if ! touch "${LOG_FILE}" 2>/dev/null; then
  LOG_FILE="/tmp/ha-panel-startup.log"
fi

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "${LOG_FILE}"; }

# ── Wait for display ──────────────────────────────────────────────────────────

log "Startup: waiting for display…"
for i in $(seq 1 30); do
  if [[ -e /dev/dri/card0 ]]; then break; fi
  sleep 1
done

# ── Detect the panel's DRM output name (DSI-1 or DSI-2 by connector) ──────────
# Read from sysfs so it works BEFORE the compositor starts — needed because
# rc.xml (touch mapping) must contain the output name at labwc launch time.

detect_panel_output() {
  local conn name
  for conn in /sys/class/drm/card*-DSI-*; do
    [[ -e "${conn}/status" ]] || continue
    if grep -qx "connected" "${conn}/status" 2>/dev/null; then
      name="$(basename "${conn}")"     # e.g. card1-DSI-2
      echo "${name#card*-}"            # → DSI-2
      return 0
    fi
  done
  echo "DSI-2"                          # sensible default for Waveshare on Pi 5
}

PANEL_OUTPUT="$(detect_panel_output)"
log "Panel output detected: ${PANEL_OUTPUT}"

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
  # ROTATION comes from /opt/ha-panel/config; 90 = portrait (default).
  # If the image is upside down, change ROTATION=90 to ROTATION=270 in the
  # config file — no code changes needed.
  local rot="${ROTATION:-90}"
  # Backlight path for screen sleep — from config, with known default
  local bl_path="${BACKLIGHT_PATH:-/sys/class/backlight/11-0045/brightness}"
  # Screen sleep timeout in seconds — override with SCREEN_SLEEP_SECS in config
  local sleep_secs="${SCREEN_SLEEP_SECS:-10}"
  mkdir -p "${LABWC_CONFIG_DIR}"

  # rc.xml: suppress window decorations + bind touch input to the panel output.
  # The touch binding is what makes touch coordinates follow the display
  # transform — without it, touch stays in unrotated landscape space.
  #
  # windowRules: Chromium's --start-maximized is unreliable under
  # ozone-wayland (window opens un-maximized, so <maximizedDecoration>
  # never applies and labwc draws a titlebar). Force the issue at the
  # compositor: strip server-side decorations from every window and
  # maximize it on map. squeekboard is a layer-shell surface, not a
  # toplevel, so it is unaffected by these rules.
  cat > "${LABWC_CONFIG_DIR}/rc.xml" <<XML
<?xml version="1.0" encoding="UTF-8"?>
<labwc_config>
  <core>
    <decoration>client</decoration>
  </core>
  <window>
    <maximizedDecoration>none</maximizedDecoration>
  </window>
  <windowRules>
    <windowRule identifier="*" serverDecoration="no">
      <action name="Maximize"/>
    </windowRule>
  </windowRules>
  <touch mapToOutput="${PANEL_OUTPUT}"/>
</labwc_config>
XML

  # autostart: rotation + screen sleep + squeekboard (OSK) + chromium loop
  # NOTE: binary is 'chromium' on Pi OS Trixie (not 'chromium-browser')
  cat > "${LABWC_CONFIG_DIR}/autostart" <<SH
# Rotate display to portrait — touch follows via rc.xml mapToOutput binding
wlr-randr --output "${PANEL_OUTPUT}" --transform ${rot} || true

# Screen sleep + auto-brightness + theme switch: backlight off after
# ${sleep_secs}s of touch inactivity, wake on the next touch (the wake gesture
# is held under an evdev grab and swallowed, so it never presses anything in
# the UI). While awake, brightness follows ambient lux from the sensor daemon
# over MQTT — tunables in ${SENSOR_CONFIG} (see screen-sleep.py header).
# The daemon also watches the retained MQTT theme topic and toggles the
# /tmp/panel-dark marker + restarts chromium on day/night changes.
# Run with the venv python so paho-mqtt is importable (evdev comes through
# --system-site-packages); falls back to system python = fixed brightness.
# Requires: python3-evdev + user in 'input' group + video-group write on the
# brightness node (udev rule, see system/install.sh).
SS_PY="${VENV_PY}"
[ -x "\${SS_PY}" ] || SS_PY="python3"
\${SS_PY} "${REPO_DIR}/system/screen-sleep.py" \\
  --timeout ${sleep_secs} \\
  --backlight "${bl_path}" \\
  --on 200 \\
  --config "${SENSOR_CONFIG}" >> "${LOG_FILE}" 2>&1 &

# On-screen keyboard
squeekboard &

# Chromium kiosk loop — restarts on crash, and when screen-sleep.py kills it
# to flip the theme. The /tmp/panel-dark marker (managed via the retained
# MQTT theme topic) adds --force-dark-mode, which makes chromium report
# prefers-color-scheme: dark so HA renders its dark theme.
while true; do
  DARK_FLAG=""
  [ -f /tmp/panel-dark ] && DARK_FLAG="--force-dark-mode"
  chromium \\
    --app="${url}" \\
    --start-maximized \\
    --noerrdialogs \\
    --disable-infobars \\
    --enable-wayland-ime \\
    --ozone-platform=wayland \\
    --no-first-run \\
    --disable-translate \\
    --disable-features=TranslateUI \\
    --check-for-update-interval=31536000 \\
    \${DARK_FLAG}
  sleep 3
done &
SH

  log "labwc config written (URL: ${url}, output: ${PANEL_OUTPUT}, rotation: ${rot}, sleep: ${sleep_secs}s)"
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

# ── Main ────────────────────────────────────────────────────────────────────

log "HA Panel startup — PID $$"

if [[ -f "${CONFIG_FILE}" ]]; then
  start_kiosk
else
  start_provisioning
fi

# Launch labwc (blocks until logout/crash)
log "Launching labwc…"
exec labwc

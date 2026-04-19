#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
#  HA Panel — SSH setup script
#  Equivalent to the touchscreen provisioning UI, for technical users.
#
#  Usage:  sudo /opt/ha-panel/repo/system/setup.sh
#
#  Writes:
#    /opt/ha-panel/config              (shell format, sourced by startup.sh)
#    /opt/ha-panel/sensor-config.py    (Python format, canonical config)
#    /opt/ha-panel/repo/sensor-daemon/config.py  (symlink → sensor-config.py)
#
#  To reconfigure an existing panel, just run this script again.
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

PANEL_BASE="/opt/ha-panel"
CONFIG_FILE="${PANEL_BASE}/config"
SENSOR_CONFIG_CANON="${PANEL_BASE}/sensor-config.py"
REPO_DIR="${PANEL_BASE}/repo"
SENSOR_CONFIG_LINK="${REPO_DIR}/sensor-daemon/config.py"

# ── Colour helpers ─────────────────────────────────────────────────────────────

BOLD="\033[1m"
DIM="\033[2m"
CYAN="\033[36m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

info()    { echo -e "  ${CYAN}→${RESET}  $*"; }
success() { echo -e "  ${GREEN}✓${RESET}  $*"; }
warn()    { echo -e "  ${YELLOW}!${RESET}  $*"; }
error()   { echo -e "  ${RED}✗${RESET}  $*" >&2; }
heading() { echo -e "\n${BOLD}$*${RESET}"; }
rule()    { echo -e "${DIM}────────────────────────────────────────────────────${RESET}"; }

# ── Root check ─────────────────────────────────────────────────────────────────

if [[ $EUID -ne 0 ]]; then
  error "This script must be run as root."
  echo  "  Run: sudo $0"
  exit 1
fi

# ── Banner ─────────────────────────────────────────────────────────────────────

clear
echo
echo -e "${BOLD}  HA Panel — Setup${RESET}"
rule
echo -e "  ${DIM}This script configures the panel to connect to your"
echo -e "  Home Assistant server and MQTT broker.${RESET}"
echo -e "  ${DIM}Existing configuration will be overwritten.${RESET}"
echo

# ── Detect current values (for defaults) ──────────────────────────────────────

CURRENT_PANEL_ID=""
CURRENT_HA_URL=""
CURRENT_MQTT_HOST=""
CURRENT_MQTT_PORT="1883"
CURRENT_MQTT_USER=""

if [[ -f "${CONFIG_FILE}" ]]; then
  warn "Existing configuration found — values will be shown as defaults."
  # shellcheck source=/dev/null
  source "${CONFIG_FILE}" 2>/dev/null || true
  CURRENT_PANEL_ID="${PANEL_ID:-}"
  CURRENT_HA_URL="${HA_URL:-}"
  CURRENT_MQTT_HOST="${MQTT_HOST:-}"
  CURRENT_MQTT_PORT="${MQTT_PORT:-1883}"
  CURRENT_MQTT_USER="${MQTT_USER:-}"
fi

# Fall back to hostname if no panel ID stored
if [[ -z "${CURRENT_PANEL_ID}" ]]; then
  CURRENT_PANEL_ID="$(hostname)"
fi

# Derive suggested HA URL and MQTT host from gateway if not set
if [[ -z "${CURRENT_HA_URL}" ]]; then
  GATEWAY="$(ip route show default 2>/dev/null | awk '/default/ { print $3; exit }')"
  if [[ -n "${GATEWAY}" ]]; then
    CURRENT_HA_URL="http://${GATEWAY}:8123"
    CURRENT_MQTT_HOST="${GATEWAY}"
  fi
fi

# ── Prompt helper ──────────────────────────────────────────────────────────────
# Usage: prompt_val "Label" "default" VARNAME [validator_function]
prompt_val() {
  local label="$1"
  local default="$2"
  local varname="$3"
  local validator="${4:-}"
  local value=""

  while true; do
    if [[ -n "${default}" ]]; then
      read -r -p "  ${label} [${default}]: " value
      value="${value:-${default}}"
    else
      read -r -p "  ${label}: " value
    fi

    if [[ -z "${value}" ]]; then
      error "This field is required."
      continue
    fi

    if [[ -n "${validator}" ]]; then
      if ! ${validator} "${value}"; then
        continue
      fi
    fi

    printf -v "${varname}" '%s' "${value}"
    break
  done
}

# Password prompt (no echo)
prompt_pass() {
  local label="$1"
  local varname="$2"
  local value=""
  local confirm=""

  while true; do
    read -r -s -p "  ${label}: " value
    echo
    if [[ -z "${value}" ]]; then
      error "Password cannot be empty."
      continue
    fi
    read -r -s -p "  Confirm ${label}: " confirm
    echo
    if [[ "${value}" != "${confirm}" ]]; then
      error "Passwords do not match. Try again."
      continue
    fi
    printf -v "${varname}" '%s' "${value}"
    break
  done
}

# ── Validators ─────────────────────────────────────────────────────────────────

validate_url() {
  if [[ "$1" != http://* && "$1" != https://* ]]; then
    error "URL must start with http:// or https://"
    return 1
  fi
  return 0
}

validate_host() {
  if [[ -z "$1" ]]; then
    error "Host cannot be empty."
    return 1
  fi
  return 0
}

validate_port() {
  if ! [[ "$1" =~ ^[0-9]+$ ]] || (( $1 < 1 || $1 > 65535 )); then
    error "Port must be a number between 1 and 65535."
    return 1
  fi
  return 0
}

validate_panel_id() {
  if ! [[ "$1" =~ ^[a-z0-9-]+$ ]]; then
    error "Panel ID must be lowercase letters, numbers and hyphens only."
    return 1
  fi
  return 0
}

# ── Collect values ─────────────────────────────────────────────────────────────

heading "  Step 1 of 4 — Home Assistant"
echo -e "  ${DIM}Enter the address of your HA server on your local network.${RESET}"
echo
prompt_val "HA Server URL" "${CURRENT_HA_URL}" NEW_HA_URL "validate_url"

heading "  Step 2 of 4 — MQTT Broker"
echo -e "  ${DIM}Usually the same server as Home Assistant.${RESET}"
echo
prompt_val "MQTT Host / IP" "${CURRENT_MQTT_HOST}" NEW_MQTT_HOST "validate_host"
prompt_val "MQTT Port"      "${CURRENT_MQTT_PORT}" NEW_MQTT_PORT "validate_port"

heading "  Step 3 of 4 — MQTT Credentials"
echo -e "  ${DIM}Create an MQTT user in HA → Settings → People.${RESET}"
echo
prompt_val "MQTT Username" "${CURRENT_MQTT_USER}" NEW_MQTT_USER
prompt_pass "MQTT Password" NEW_MQTT_PASS

heading "  Step 4 of 4 — Panel Identity"
echo -e "  ${DIM}Unique ID for this panel. Used as the device name in HA.${RESET}"
echo
prompt_val "Panel ID" "${CURRENT_PANEL_ID}" NEW_PANEL_ID "validate_panel_id"

# ── Review ─────────────────────────────────────────────────────────────────────

echo
rule
echo -e "${BOLD}  Review${RESET}"
rule
echo
echo -e "  ${DIM}HA URL      ${RESET}  ${NEW_HA_URL}"
echo -e "  ${DIM}MQTT Host   ${RESET}  ${NEW_MQTT_HOST}"
echo -e "  ${DIM}MQTT Port   ${RESET}  ${NEW_MQTT_PORT}"
echo -e "  ${DIM}MQTT User   ${RESET}  ${NEW_MQTT_USER}"
echo -e "  ${DIM}MQTT Pass   ${RESET}  ••••••••"
echo -e "  ${DIM}Panel ID    ${RESET}  ${NEW_PANEL_ID}"
echo
read -r -p "  Save and reboot? [y/N] " CONFIRM
echo

if [[ "${CONFIRM,,}" != "y" ]]; then
  warn "Aborted — no changes written."
  exit 0
fi

# ── Detect backlight path ──────────────────────────────────────────────────────

BACKLIGHT_PATH=""
if [[ -d /sys/class/backlight ]]; then
  for entry in /sys/class/backlight/*/brightness; do
    if [[ -f "${entry}" ]]; then
      BACKLIGHT_PATH="${entry}"
      break
    fi
  done
fi
BACKLIGHT_PATH="${BACKLIGHT_PATH:-/sys/class/backlight/11-0045/brightness}"
info "Backlight path: ${BACKLIGHT_PATH}"

# ── Write /opt/ha-panel/config ─────────────────────────────────────────────────

info "Writing ${CONFIG_FILE} …"
mkdir -p "${PANEL_BASE}"

cat > "${CONFIG_FILE}" <<EOF
# HA Panel runtime configuration
# Generated by setup.sh — run 'sudo setup.sh' to reconfigure
#
PANEL_ID=${NEW_PANEL_ID}
HA_URL=${NEW_HA_URL}
MQTT_HOST=${NEW_MQTT_HOST}
MQTT_PORT=${NEW_MQTT_PORT}
MQTT_USER=${NEW_MQTT_USER}
MQTT_PASS=${NEW_MQTT_PASS}
BACKLIGHT_PATH=${BACKLIGHT_PATH}
EOF

chmod 600 "${CONFIG_FILE}"
success "Wrote ${CONFIG_FILE}"

# ── Write /opt/ha-panel/sensor-config.py ──────────────────────────────────────

info "Writing ${SENSOR_CONFIG_CANON} …"

cat > "${SENSOR_CONFIG_CANON}" <<PYEOF
# Sensor daemon configuration
# Generated by setup.sh — run 'sudo setup.sh' to reconfigure
# Canonical location: /opt/ha-panel/sensor-config.py
# Linked into repo at: sensor-daemon/config.py
# This file must NEVER be overwritten by git operations.

PANEL_ID = "${NEW_PANEL_ID}"

# MQTT
MQTT_BROKER   = "${NEW_MQTT_HOST}"
MQTT_PORT     = ${NEW_MQTT_PORT}
MQTT_USERNAME = "${NEW_MQTT_USER}"
MQTT_PASSWORD = "${NEW_MQTT_PASS}"

# I2C bus
I2C_BUS = 1

# Sensor I2C addresses (do not change unless you know why)
BME680_I2C_ADDR   = 0x77   # SDO pulled high on this breakout
VEML6030_I2C_ADDR = 0x48   # ADDR pin pulled high on this breakout
VL53L0X_I2C_ADDR  = 0x29
AT42QT1070_I2C_ADDR = 0x1B

# Calibration offsets — adjust after burn-in if needed
TEMPERATURE_OFFSET = 0.0  # degrees C
HUMIDITY_OFFSET    = 0.0  # percent RH

BACKLIGHT_PATH = "${BACKLIGHT_PATH}"
PYEOF

chmod 600 "${SENSOR_CONFIG_CANON}"
success "Wrote ${SENSOR_CONFIG_CANON}"

# ── Symlink into repo (protected from git reset --hard) ───────────────────────

if [[ -d "${REPO_DIR}/sensor-daemon" ]]; then
  if [[ -e "${SENSOR_CONFIG_LINK}" || -L "${SENSOR_CONFIG_LINK}" ]]; then
    rm -f "${SENSOR_CONFIG_LINK}"
  fi
  ln -s "${SENSOR_CONFIG_CANON}" "${SENSOR_CONFIG_LINK}"
  success "Symlinked ${SENSOR_CONFIG_LINK} → ${SENSOR_CONFIG_CANON}"
else
  warn "Repo not yet cloned — symlink will be created by install.sh on next run."
fi

# ── Done ───────────────────────────────────────────────────────────────────────

echo
rule
success "Configuration saved."
echo
echo -e "  The panel will reboot and connect to Home Assistant automatically."
echo -e "  ${DIM}HA dashboard: ${NEW_HA_URL}${RESET}"
echo
rule
echo

sleep 2
reboot

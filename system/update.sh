#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
#  HA Panel — Nightly update script
#  Triggered by panel-update.timer at 2:00–2:05am.
#
#  Order of operations:
#    1. Screen off
#    2. apt upgrade
#    3. rpi-eeprom update
#    4. pip upgrade (venv)
#    5. Protect sensor-config.py  ← before git
#    6. git reset --hard origin/main
#    7. Restore sensor-config.py symlink
#    8. Reboot if kernel/eeprom changed
#    9. Screen on
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

PANEL_BASE="/opt/ha-panel"
CONFIG_FILE="${PANEL_BASE}/config"
SENSOR_CONFIG_CANON="${PANEL_BASE}/sensor-config.py"
REPO_DIR="${PANEL_BASE}/repo"
SENSOR_CONFIG_LINK="${REPO_DIR}/sensor-daemon/config.py"
VENV="${PANEL_BASE}/venv"

LOG_FILE="/var/log/ha-panel-update.log"

log()  { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "${LOG_FILE}"; }
err()  { echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: $*" | tee -a "${LOG_FILE}" >&2; }

# ── Backlight helpers ─────────────────────────────────────────────────────────

screen_off() {
  local bl_path
  bl_path="$(backlight_path)"
  if [[ -f "${bl_path}" ]]; then
    echo 0 > "${bl_path}" 2>/dev/null || true
    log "Screen off (${bl_path})"
  fi
}

screen_on() {
  local bl_path
  bl_path="$(backlight_path)"
  if [[ -f "${bl_path}" ]]; then
    echo 200 > "${bl_path}" 2>/dev/null || true
    log "Screen on (${bl_path})"
  fi
}

backlight_path() {
  # Source config for BACKLIGHT_PATH if available
  if [[ -f "${CONFIG_FILE}" ]]; then
    # shellcheck source=/dev/null
    local BACKLIGHT_PATH=""
    source "${CONFIG_FILE}" 2>/dev/null || true
    if [[ -n "${BACKLIGHT_PATH:-}" && -f "${BACKLIGHT_PATH}" ]]; then
      echo "${BACKLIGHT_PATH}"
      return
    fi
  fi

  # Auto-detect from sysfs
  for entry in /sys/class/backlight/*/brightness; do
    if [[ -f "${entry}" ]]; then
      echo "${entry}"
      return
    fi
  done

  # Known fallback for Waveshare 8" DSI on Pi 5
  echo "/sys/class/backlight/11-0045/brightness"
}

# ── Config protection ─────────────────────────────────────────────────────────

protect_sensor_config() {
  # The canonical sensor config lives at /opt/ha-panel/sensor-config.py,
  # outside the repo directory. git reset --hard cannot touch it.
  # This function verifies the canonical file exists and re-links it if needed.

  if [[ ! -f "${SENSOR_CONFIG_CANON}" ]]; then
    log "WARNING: ${SENSOR_CONFIG_CANON} not found — sensor config may be lost."
    log "Run 'sudo setup.sh' to reconfigure after this update."
    return 0
  fi

  log "Canonical sensor config present: ${SENSOR_CONFIG_CANON}"
}

restore_sensor_config_link() {
  # After git reset, the symlink in the repo may have been reset to the
  # example template or removed. Re-create the symlink to the canonical file.

  if [[ ! -f "${SENSOR_CONFIG_CANON}" ]]; then
    log "No canonical sensor config to restore — skipping symlink."
    return 0
  fi

  if [[ -e "${SENSOR_CONFIG_LINK}" || -L "${SENSOR_CONFIG_LINK}" ]]; then
    # If it's already a symlink to the canonical file, leave it
    if [[ -L "${SENSOR_CONFIG_LINK}" ]]; then
      local target
      target="$(readlink "${SENSOR_CONFIG_LINK}")"
      if [[ "${target}" == "${SENSOR_CONFIG_CANON}" ]]; then
        log "Sensor config symlink is correct — no change needed."
        return 0
      fi
    fi
    rm -f "${SENSOR_CONFIG_LINK}"
  fi

  ln -s "${SENSOR_CONFIG_CANON}" "${SENSOR_CONFIG_LINK}"
  log "Restored symlink: ${SENSOR_CONFIG_LINK} → ${SENSOR_CONFIG_CANON}"
}

# ── Main ──────────────────────────────────────────────────────────────────────

log "─── Update started ───────────────────────────────────────"

NEEDS_REBOOT=0

# 1. Screen off
screen_off

# 2. apt upgrade
log "Running apt upgrade…"
apt-get update -qq >> "${LOG_FILE}" 2>&1 || err "apt-get update failed"
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq >> "${LOG_FILE}" 2>&1 || err "apt-get upgrade failed"
log "apt upgrade complete."

# 3. rpi-eeprom
log "Checking rpi-eeprom…"
EEPROM_BEFORE="$(rpi-eeprom-update 2>/dev/null | grep 'CURRENT:' || true)"
rpi-eeprom-update -a >> "${LOG_FILE}" 2>&1 || true
EEPROM_AFTER="$(rpi-eeprom-update 2>/dev/null | grep 'CURRENT:' || true)"
if [[ "${EEPROM_BEFORE}" != "${EEPROM_AFTER}" ]]; then
  log "EEPROM updated — reboot required."
  NEEDS_REBOOT=1
fi

# 4. Python venv packages
if [[ -d "${VENV}" && -f "${REPO_DIR}/sensor-daemon/requirements.txt" ]]; then
  log "Upgrading Python packages…"
  "${VENV}/bin/pip" install --upgrade --quiet \
    -r "${REPO_DIR}/sensor-daemon/requirements.txt" >> "${LOG_FILE}" 2>&1 \
    || err "pip upgrade failed"
  log "Python packages up to date."
fi

# 5. Protect sensor config BEFORE git operations
protect_sensor_config

# 6. Pull latest repo
log "Pulling latest repo…"
git -C "${REPO_DIR}" fetch --quiet origin >> "${LOG_FILE}" 2>&1 || { err "git fetch failed"; screen_on; exit 1; }
git -C "${REPO_DIR}" reset --hard origin/main >> "${LOG_FILE}" 2>&1 || { err "git reset failed"; screen_on; exit 1; }
log "Repo updated to $(git -C "${REPO_DIR}" rev-parse --short HEAD)."

# 7. Restore sensor config symlink after git reset
restore_sensor_config_link

# Restart sensor daemon to pick up any code changes
log "Restarting sensor-daemon…"
systemctl restart sensor-daemon >> "${LOG_FILE}" 2>&1 || err "sensor-daemon restart failed"

# 8. Reboot if kernel or eeprom changed
CURRENT_KERNEL="$(uname -r)"
INSTALLED_KERNEL="$(ls /boot/firmware/kernel*.img 2>/dev/null | head -1 || true)"
# Simple heuristic: if apt upgraded a kernel package, reboot
if apt-get --simulate upgrade 2>/dev/null | grep -q "linux-image"; then
  log "Kernel upgrade pending — reboot required."
  NEEDS_REBOOT=1
fi

log "─── Update complete ──────────────────────────────────────"

if [[ "${NEEDS_REBOOT}" -eq 1 ]]; then
  log "Rebooting in 10 seconds…"
  sleep 10
  reboot
else
  screen_on
  log "Screen on — update complete, no reboot needed."
fi

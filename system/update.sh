#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
#  HA Panel — Nightly update script
#  Triggered by panel-update.timer at 2:00–2:05am.
#
#  Order of operations:
#    1. Screen off + switch kiosk to the update splash
#    2. apt full-upgrade (fully unattended, conffile prompts suppressed)
#    3. rpi-eeprom update
#    4. pip upgrade (venv)
#    5. Protect sensor-config.py  ← before git
#    6. git reset --hard origin/main
#    7. Restore ownership + sensor-config.py symlink
#    8. Reboot if kernel/eeprom changed
#    9. Return kiosk to the dashboard; screen stays off until touched
#
#  Splash: /run/ha-panel-updating marks an update in progress — the chromium
#  loop in labwc autostart shows system/update-splash.html while it exists.
#  Progress is written to /run/ha-panel-update-status.js, which the splash
#  polls once a second. The screen stays dark throughout (screen-sleep owns
#  the backlight); anyone touching the panel mid-update wakes it onto the
#  splash instead of what would look like a dead dashboard.
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

PANEL_BASE="/opt/ha-panel"
CONFIG_FILE="${PANEL_BASE}/config"
SENSOR_CONFIG_CANON="${PANEL_BASE}/sensor-config.py"
REPO_DIR="${PANEL_BASE}/repo"
SENSOR_CONFIG_LINK="${REPO_DIR}/sensor-daemon/config.py"
VENV="${PANEL_BASE}/venv"

LOG_FILE="/var/log/ha-panel-update.log"
UPDATE_MARKER="/run/ha-panel-updating"
STATUS_JS="/run/ha-panel-update-status.js"

log()  { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "${LOG_FILE}"; }
err()  { echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: $*" | tee -a "${LOG_FILE}" >&2; }

# Fully unattended apt: never prompt, keep existing conffiles on conflict
# (--force-confdef prefers the default action; --force-confold keeps the
#  local file when there is no default — together they suppress every
#  interactive dpkg conffile question).
APT_OPTS=(-y -qq
  -o "Dpkg::Options::=--force-confdef"
  -o "Dpkg::Options::=--force-confold")

# ── Splash helpers ────────────────────────────────────────────────────────────

splash_status() {  # $1 = percent (0–100), $2 = one-line message
  printf 'window.updateStatus={pct:%s,message:"%s",ts:%s};\n' \
    "$1" "$2" "$(date +%s)" > "${STATUS_JS}" 2>/dev/null || true
  chmod 644 "${STATUS_JS}" 2>/dev/null || true
}

splash_begin() {
  touch "${UPDATE_MARKER}"
  chmod 644 "${UPDATE_MARKER}" 2>/dev/null || true
  splash_status 3 "Preparing…"
  # Bounce chromium — the kiosk loop relaunches it onto the splash page
  pkill -x chromium 2>/dev/null || true
}

splash_end() {
  rm -f "${UPDATE_MARKER}" "${STATUS_JS}"
  # Bounce chromium back to the dashboard
  pkill -x chromium 2>/dev/null || true
}

# Always clear the splash on any exit (success, error, or reboot path —
# /run is tmpfs so a reboot clears the files regardless).
trap splash_end EXIT

# ── Backlight helpers ─────────────────────────────────────────────────────────

screen_off() {
  local bl_path
  bl_path="$(backlight_path)"
  if [[ -f "${bl_path}" ]]; then
    echo 0 > "${bl_path}" 2>/dev/null || true
    log "Screen off (${bl_path})"
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

restore_repo_ownership() {
  # This script runs as root (apt/systemctl/reboot need it), so files written
  # by git reset above are root-owned. The panel user must keep full control
  # of the repo for manual deploys — restore ownership to whoever owns the
  # panel base directory.
  local owner
  owner="$(stat -c '%U:%G' "${PANEL_BASE}" 2>/dev/null || true)"
  if [[ -n "${owner}" && "${owner}" != "root:root" ]]; then
    chown -R "${owner}" "${REPO_DIR}"
    log "Repo ownership restored to ${owner}."
  fi
}

# ── Kernel change detection ───────────────────────────────────────────────────

kernel_fingerprint() {
  # Version fingerprint of every installed kernel package. Compared before
  # and after the upgrade — any change means a new kernel was installed and
  # a reboot is required to run it.
  # NOTE: dpkg-query exits non-zero when ANY pattern matches nothing (the
  # legacy raspberrypi-kernel*/rpi-kernel* names don't exist on Trixie), so
  # the || true is load-bearing under set -euo pipefail.
  { dpkg-query -W 'linux-image*' 'raspberrypi-kernel*' 'rpi-kernel*' 2>/dev/null || true; } \
    | sort | md5sum | cut -d' ' -f1
}

# ── Main ──────────────────────────────────────────────────────────────────────

log "─── Update started ───────────────────────────────────────"

NEEDS_REBOOT=0

# 1. Screen off + splash. The screen stays dark; a touch wakes it onto the
#    update splash instead of a stale dashboard.
screen_off
splash_begin

# 2. apt full-upgrade — dist-upgrade so packages needing new/removed
#    dependencies (kernel-related on Pi OS) are never held back.
splash_status 8 "Refreshing package lists…"
log "Running apt full-upgrade…"
KERNEL_BEFORE="$(kernel_fingerprint)"
apt-get update -qq >> "${LOG_FILE}" 2>&1 || err "apt-get update failed"
splash_status 15 "Upgrading system packages — this is the long part…"
DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade "${APT_OPTS[@]}" >> "${LOG_FILE}" 2>&1 || err "apt-get dist-upgrade failed"
splash_status 55 "Removing obsolete packages…"
DEBIAN_FRONTEND=noninteractive apt-get autoremove --purge "${APT_OPTS[@]}" >> "${LOG_FILE}" 2>&1 || err "apt-get autoremove failed"
KERNEL_AFTER="$(kernel_fingerprint)"
log "apt full-upgrade complete."

# 3. rpi-eeprom
splash_status 62 "Checking firmware…"
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
  splash_status 72 "Updating Python components…"
  log "Upgrading Python packages…"
  "${VENV}/bin/pip" install --upgrade --quiet \
    -r "${REPO_DIR}/sensor-daemon/requirements.txt" >> "${LOG_FILE}" 2>&1 \
    || err "pip upgrade failed"
  log "Python packages up to date."
fi

# 5. Protect sensor config BEFORE git operations
protect_sensor_config

# 6. Pull latest repo
splash_status 82 "Syncing panel software…"
log "Pulling latest repo…"
git -C "${REPO_DIR}" fetch --quiet origin >> "${LOG_FILE}" 2>&1 || { err "git fetch failed"; exit 1; }
git -C "${REPO_DIR}" reset --hard origin/main >> "${LOG_FILE}" 2>&1 || { err "git reset failed"; exit 1; }
log "Repo updated to $(git -C "${REPO_DIR}" rev-parse --short HEAD)."

# 7. Restore ownership + sensor config symlink after git reset
restore_repo_ownership
restore_sensor_config_link

# Restart sensor daemon to pick up any code changes
splash_status 92 "Restarting services…"
log "Restarting sensor-daemon…"
systemctl restart sensor-daemon >> "${LOG_FILE}" 2>&1 || err "sensor-daemon restart failed"

# 8. Reboot if a kernel was installed, the running kernel's modules are gone,
#    the system requests it, or the eeprom changed (flag set above).
if [[ "${KERNEL_BEFORE}" != "${KERNEL_AFTER}" ]]; then
  log "Kernel package changed during upgrade — reboot required."
  NEEDS_REBOOT=1
fi
if [[ ! -d "/lib/modules/$(uname -r)" ]]; then
  log "Running kernel's modules directory removed by upgrade — reboot required."
  NEEDS_REBOOT=1
fi
if [[ -f /run/reboot-required ]]; then
  log "/run/reboot-required present — reboot required."
  NEEDS_REBOOT=1
fi

splash_status 100 "Finishing…"
log "─── Update complete ──────────────────────────────────────"

if [[ "${NEEDS_REBOOT}" -eq 1 ]]; then
  log "Rebooting in 10 seconds…"
  sleep 10
  reboot
else
  # Backlight deliberately left off — screen-sleep owns it and wakes the
  # screen on the next touch. (Writing it on here would leave the panel lit
  # all night while screen-sleep still holds its input grab.)
  log "Update finished — kiosk returned to dashboard, screen off until touched."
fi

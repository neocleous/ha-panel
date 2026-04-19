#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
#  HA Panel — System install script  (V2)
#
#  Run on a freshly flashed Pi OS Lite 64-bit (Trixie) after SSH login:
#
#    curl -fsSL https://raw.githubusercontent.com/neocleous/ha-panel/main/system/install.sh \
#      -o /tmp/install.sh && sudo bash /tmp/install.sh
#
#  (Must be saved to a file first — piping to sudo bash breaks read prompts.)
#
#  What this script does:
#    1. Verify platform and root
#    2. Confirm or change hostname / panel ID
#    3. Install apt packages
#    4. Configure: display overlay, I2C, Bluetooth off, TTY1 autologin
#    5. Add user to required groups
#    6. Clone or update repo → /opt/ha-panel/repo
#    7. Create Python venv (--system-site-packages for lgpio)
#    8. Install systemd services
#    9. Create ~/.bash_profile kiosk hook
#   10. Configure nftables firewall
#   11. Configure unattended-upgrades
#   12. Offer reboot
#
#  V2 changes from V1:
#    - Removed config prompts (HA URL, MQTT) — handled by provisioning UI
#    - Added nmcli (network-manager) to apt packages
#    - Venv uses --system-site-packages (required for lgpio)
#    - Creates sensor-config.py symlink if canonical config already exists
#    - Firewall subnet auto-detected from default gateway (not hardcoded)
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO_URL="https://github.com/neocleous/ha-panel.git"
PANEL_BASE="/opt/ha-panel"
REPO_DIR="${PANEL_BASE}/repo"
VENV_DIR="${PANEL_BASE}/venv"
SENSOR_CONFIG_CANON="${PANEL_BASE}/sensor-config.py"
SENSOR_CONFIG_LINK="${REPO_DIR}/sensor-daemon/config.py"

LOG_FILE="/var/log/ha-panel-install.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

# ── Colours ───────────────────────────────────────────────────────────────────

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
err()     { echo -e "  ${RED}✗${RESET}  $*" >&2; }
heading() { echo; echo -e "${BOLD}  $*${RESET}"; echo -e "  ${DIM}$(printf '─%.0s' $(seq 1 50))${RESET}"; }
step()    { echo; echo -e "${BOLD}  [$((STEP_N++))]${RESET}  $*"; }
STEP_N=1

# ── Preflight ─────────────────────────────────────────────────────────────────

if [[ $EUID -ne 0 ]]; then
  err "Run this script with sudo."
  exit 1
fi

if [[ "$(uname -m)" != "aarch64" ]]; then
  err "This script requires a 64-bit ARM system (aarch64). Got: $(uname -m)"
  exit 1
fi

# Detect calling user (works correctly inside sudo)
PANEL_USER="$(logname 2>/dev/null || echo "${SUDO_USER:-pi}")"
PANEL_HOME="$(getent passwd "${PANEL_USER}" | cut -d: -f6)"

if [[ -z "${PANEL_USER}" ]]; then
  err "Could not detect calling user. Run with sudo from your user account."
  exit 1
fi

# ── Banner ────────────────────────────────────────────────────────────────────

clear
echo
echo -e "${BOLD}  HA Panel — Install (V2)${RESET}"
echo -e "  ${DIM}Installing as user: ${PANEL_USER}  |  Home: ${PANEL_HOME}${RESET}"
echo

# ── Step 1: Hostname / Panel ID ───────────────────────────────────────────────

step "Panel hostname"
CURRENT_HOSTNAME="$(hostname)"
echo
echo -e "  Current hostname: ${BOLD}${CURRENT_HOSTNAME}${RESET}"
read -r -p "  Change it? Enter new hostname or press Enter to keep [${CURRENT_HOSTNAME}]: " NEW_HOSTNAME
NEW_HOSTNAME="${NEW_HOSTNAME:-${CURRENT_HOSTNAME}}"

if [[ "${NEW_HOSTNAME}" != "${CURRENT_HOSTNAME}" ]]; then
  if ! [[ "${NEW_HOSTNAME}" =~ ^[a-z0-9-]+$ ]]; then
    err "Hostname must be lowercase letters, numbers and hyphens only."
    exit 1
  fi
  hostnamectl set-hostname "${NEW_HOSTNAME}"
  # Update /etc/hosts
  sed -i "s/127\.0\.1\.1\s.*/127.0.1.1\t${NEW_HOSTNAME}/" /etc/hosts
  success "Hostname set to ${NEW_HOSTNAME}"
else
  info "Keeping hostname: ${CURRENT_HOSTNAME}"
fi

# ── Step 2: apt packages ──────────────────────────────────────────────────────

step "Installing packages"

APT_PACKAGES=(
  # Display / Wayland stack
  labwc
  squeekboard
  chromium-browser
  xdg-utils

  # Network
  network-manager          # provides nmcli for Wi-Fi provisioning
  curl
  wget

  # I2C / GPIO
  python3-smbus2
  i2c-tools
  python3-lgpio            # lgpio — only available as system package, not via pip

  # Python
  python3
  python3-pip
  python3-venv
  python3-full

  # System
  git
  unattended-upgrades
  apt-listchanges
  nftables

  # rpi tools
  raspi-config
  rpi-eeprom
)

apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -q "${APT_PACKAGES[@]}"
success "Packages installed"

# ── Step 3: Boot configuration ────────────────────────────────────────────────

step "Configuring boot"

CONFIG_TXT="/boot/firmware/config.txt"

# Waveshare 8" DSI display overlay
if ! grep -q "vc4-kms-dsi-waveshare-panel" "${CONFIG_TXT}" 2>/dev/null; then
  echo "dtoverlay=vc4-kms-dsi-waveshare-panel,8_0_inch" >> "${CONFIG_TXT}"
  info "Added DSI display overlay"
fi

# I2C bus 1
raspi-config nonint do_i2c 0
info "I2C enabled"

# Disable Bluetooth (not used, saves power)
if ! grep -q "dtoverlay=disable-bt" "${CONFIG_TXT}" 2>/dev/null; then
  echo "dtoverlay=disable-bt" >> "${CONFIG_TXT}"
  info "Bluetooth disabled"
fi

# TTY1 autologin (required for Wayland kiosk — do NOT use systemd user services)
raspi-config nonint do_boot_behaviour B2
success "TTY1 autologin configured"

# ── Step 4: User groups ───────────────────────────────────────────────────────

step "Adding ${PANEL_USER} to required groups"

for GROUP in video input render spi i2c gpio; do
  if getent group "${GROUP}" > /dev/null 2>&1; then
    usermod -aG "${GROUP}" "${PANEL_USER}"
    info "Added to group: ${GROUP}"
  else
    warn "Group ${GROUP} does not exist — skipping"
  fi
done

success "Group membership updated"

# ── Step 5: Clone or update repo ──────────────────────────────────────────────

step "Setting up repository"

mkdir -p "${PANEL_BASE}"

if [[ -d "${REPO_DIR}/.git" ]]; then
  info "Repo already cloned — pulling latest…"
  git -C "${REPO_DIR}" fetch --quiet origin
  git -C "${REPO_DIR}" reset --hard origin/main
  success "Repo updated"
else
  info "Cloning repo…"
  git clone --quiet "${REPO_URL}" "${REPO_DIR}"
  success "Repo cloned to ${REPO_DIR}"
fi

# Fix ownership
chown -R "${PANEL_USER}:${PANEL_USER}" "${PANEL_BASE}"

# ── Step 6: Python venv ───────────────────────────────────────────────────────

step "Creating Python venv"

# --system-site-packages is required so lgpio (system package only) is accessible
if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv --system-site-packages "${VENV_DIR}"
  success "Venv created (with --system-site-packages)"
else
  info "Venv already exists"
fi

"${VENV_DIR}/bin/pip" install --upgrade --quiet pip
"${VENV_DIR}/bin/pip" install --quiet -r "${REPO_DIR}/sensor-daemon/requirements.txt"
success "Python dependencies installed"

# ── Step 7: Sensor config symlink (if canonical config already exists) ────────

step "Sensor config"

if [[ -f "${SENSOR_CONFIG_CANON}" ]]; then
  if [[ -e "${SENSOR_CONFIG_LINK}" || -L "${SENSOR_CONFIG_LINK}" ]]; then
    rm -f "${SENSOR_CONFIG_LINK}"
  fi
  ln -s "${SENSOR_CONFIG_CANON}" "${SENSOR_CONFIG_LINK}"
  success "Symlinked sensor config (from prior configuration)"
else
  info "No sensor config yet — will be created by provisioning UI at first boot"
fi

# ── Step 8: systemd services ──────────────────────────────────────────────────

step "Installing systemd services"

SERVICES_SRC="${REPO_DIR}/system"

cp "${SERVICES_SRC}/sensor-daemon.service"  /etc/systemd/system/
cp "${SERVICES_SRC}/panel-update.service"   /etc/systemd/system/
cp "${SERVICES_SRC}/panel-update.timer"     /etc/systemd/system/

systemctl daemon-reload
systemctl enable sensor-daemon
systemctl enable panel-update.timer
systemctl start  panel-update.timer

success "Services installed and enabled"

# ── Step 9: ~/.bash_profile kiosk hook ───────────────────────────────────────

step "Setting up kiosk autostart"

BASH_PROFILE="${PANEL_HOME}/.bash_profile"

KIOSK_BLOCK="
# ── HA Panel kiosk startup ─────────────────────────────────────────────────
if [[ \"\$(tty)\" == '/dev/tty1' ]]; then
  exec bash ${REPO_DIR}/system/startup.sh
fi
# ──────────────────────────────────────────────────────────────────────────
"

if grep -q "ha-panel" "${BASH_PROFILE}" 2>/dev/null; then
  info "Kiosk hook already present in ~/.bash_profile"
else
  echo "${KIOSK_BLOCK}" >> "${BASH_PROFILE}"
  chown "${PANEL_USER}:${PANEL_USER}" "${BASH_PROFILE}"
  success "Kiosk hook added to ~/.bash_profile"
fi

# ── Step 10: nftables firewall ────────────────────────────────────────────────

step "Configuring firewall"

# Detect local subnet from default gateway
GATEWAY="$(ip route show default 2>/dev/null | awk '/default/ { print $3; exit }' || true)"
LOCAL_SUBNET=""

if [[ -n "${GATEWAY}" ]]; then
  IFS='.' read -r -a GW_PARTS <<< "${GATEWAY}"
  if [[ ${#GW_PARTS[@]} -eq 4 ]]; then
    LOCAL_SUBNET="${GW_PARTS[0]}.${GW_PARTS[1]}.${GW_PARTS[2]}.0/24"
  fi
fi

if [[ -z "${LOCAL_SUBNET}" ]]; then
  warn "Could not detect local subnet — defaulting to 192.168.0.0/16"
  LOCAL_SUBNET="192.168.0.0/16"
fi

info "Local subnet: ${LOCAL_SUBNET}"

cat > /etc/nftables.conf <<NFTEOF
#!/usr/sbin/nft -f
# HA Panel firewall — generated by install.sh

flush ruleset

table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;

    # Loopback
    iif lo accept

    # Established / related
    ct state established,related accept

    # ICMP
    ip  protocol icmp  accept
    ip6 nexthdr  icmpv6 accept

    # SSH from local network only
    ip saddr ${LOCAL_SUBNET} tcp dport 22 accept

    # Provisioning server (localhost only — already bound to 127.0.0.1)
    # No external access needed

    # Drop everything else
    drop
  }

  chain forward {
    type filter hook forward priority 0; policy drop;
  }

  chain output {
    type filter hook output priority 0; policy accept;
  }
}
NFTEOF

systemctl enable nftables
systemctl restart nftables
success "Firewall configured (SSH allowed from ${LOCAL_SUBNET})"

# ── Step 11: Unattended upgrades ──────────────────────────────────────────────

step "Configuring unattended upgrades"

cat > /etc/apt/apt.conf.d/20ha-panel-upgrades <<APT
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "0";
APT
# Nightly upgrades handled by panel-update.timer instead

success "Unattended upgrades configured"

# ── Done ──────────────────────────────────────────────────────────────────────

echo
echo -e "  ${DIM}$(printf '─%.0s' $(seq 1 50))${RESET}"
echo
echo -e "${BOLD}  Install complete!${RESET}"
echo
echo -e "  ${CYAN}Next steps:${RESET}"
echo -e "    1. Reboot the panel."
echo -e "    2. The touchscreen will show the setup wizard."
echo -e "    3. Enter your HA URL, MQTT details, and panel name."
echo -e "    4. The panel will reboot and connect to Home Assistant."
echo
echo -e "  ${DIM}SSH alternative: after reboot, run${RESET}"
echo -e "    sudo ${REPO_DIR}/system/setup.sh"
echo
echo -e "  ${DIM}Logs: ${LOG_FILE}${RESET}"
echo

read -r -p "  Reboot now? [y/N] " DO_REBOOT
echo

if [[ "${DO_REBOOT,,}" == "y" ]]; then
  info "Rebooting…"
  reboot
else
  warn "Remember to reboot before the panel will work correctly."
fi

#!/bin/bash
set -e

# ─────────────────────────────────────────────
# HA Panel — Install Script
# Tested on: Raspberry Pi OS Lite 64-bit (Trixie)
# Hardware:  Raspberry Pi 5 + Waveshare 8" DSI
# ─────────────────────────────────────────────

REPO_URL="https://github.com/neocleous/ha-panel.git"
REPO_DIR="/opt/ha-panel/repo"
VENV_DIR="/opt/ha-panel/venv"
HA_URL="http://192.168.1.145:8123"
MQTT_HOST="192.168.1.145"
MQTT_PORT="1883"
MQTT_USER="ha-panel"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()     { echo -e "${GREEN}[✓]${NC} $1"; }
info()    { echo -e "${BLUE}[→]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; exit 1; }
section() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }

# ─────────────────────────────────────────────
# Preflight checks
# ─────────────────────────────────────────────

section "Preflight"

[ "$(id -u)" != "0" ] && error "Run as root: sudo bash install.sh"
[ "$(uname -m)" != "aarch64" ] && error "This script requires a 64-bit ARM system (aarch64)"

# Detect the calling user (the user who invoked sudo)
PANEL_USER=$(logname 2>/dev/null || echo "${SUDO_USER:-pi}")
PANEL_HOME="/home/${PANEL_USER}"
info "Detected user: ${PANEL_USER}"

PANEL_ID=$(hostname)
info "Panel ID detected from hostname: ${PANEL_ID}"
read -rp "    Use '${PANEL_ID}' as the panel ID? [Y/n] " confirm
if [[ "$confirm" =~ ^[Nn]$ ]]; then
    read -rp "    Enter panel ID (e.g. panel-02): " PANEL_ID
    hostnamectl set-hostname "$PANEL_ID"
    log "Hostname updated to ${PANEL_ID}"
else
    log "Using hostname: ${PANEL_ID}"
fi

# ─────────────────────────────────────────────
# System packages
# ─────────────────────────────────────────────

section "System packages"

info "Updating package lists..."
apt-get update -qq

info "Installing required packages..."
apt-get install -y -qq \
    labwc \
    cage \
    chromium \
    squeekboard \
    seatd \
    wlr-randr \
    wayland-utils \
    libinput-tools \
    python3-venv \
    python3-pip \
    python3-smbus \
    i2c-tools \
    git \
    curl \
    nftables \
    unattended-upgrades \
    swig \
    liblgpio-dev

log "Packages installed"

# ─────────────────────────────────────────────
# Boot configuration
# ─────────────────────────────────────────────

section "Boot configuration"

CONFIG=/boot/firmware/config.txt

info "Configuring display overlay..."
if ! grep -q "vc4-kms-dsi-waveshare-panel" "$CONFIG"; then
    echo "dtoverlay=vc4-kms-dsi-waveshare-panel,8_0_inch" >> "$CONFIG"
    log "Display overlay added"
else
    log "Display overlay already present"
fi

info "Disabling Bluetooth..."
if ! grep -q "disable-bt" "$CONFIG"; then
    echo "dtoverlay=disable-bt" >> "$CONFIG"
    log "Bluetooth disabled"
else
    log "Bluetooth already disabled"
fi

info "Enabling I2C..."
raspi-config nonint do_i2c 0
log "I2C enabled"

info "Configuring autologin on TTY1..."
raspi-config nonint do_boot_behaviour B2
log "Autologin configured"

# ─────────────────────────────────────────────
# User groups
# ─────────────────────────────────────────────

section "User groups"

for group in video input render spi i2c gpio; do
    if ! groups "${PANEL_USER}" | grep -q "$group"; then
        usermod -aG "$group" "${PANEL_USER}"
        log "Added ${PANEL_USER} to group: ${group}"
    else
        log "${PANEL_USER} already in group: ${group}"
    fi
done

# ─────────────────────────────────────────────
# Clone repo (public, no deploy key needed)
# ─────────────────────────────────────────────

section "Cloning repository"

mkdir -p /opt/ha-panel
chown "${PANEL_USER}:${PANEL_USER}" /opt/ha-panel

if [ ! -d "$REPO_DIR" ]; then
    info "Cloning repo to ${REPO_DIR}..."
    sudo -u "${PANEL_USER}" git clone "$REPO_URL" "$REPO_DIR"
    log "Repository cloned"
else
    info "Repo already exists, pulling latest..."
    sudo -u "${PANEL_USER}" git -C "$REPO_DIR" pull
    log "Repository updated"
fi

# Make scripts executable
chmod +x "${REPO_DIR}/system/startup.sh"
chmod +x "${REPO_DIR}/system/update.sh" 2>/dev/null || true
chown -R "${PANEL_USER}:${PANEL_USER}" "$REPO_DIR"
log "Permissions set"

# Git hooks to restore executable permissions on pull
info "Installing git hooks..."
cat > "${REPO_DIR}/.git/hooks/post-merge" << 'HOOK'
#!/bin/bash
chmod +x /opt/ha-panel/repo/system/*.sh 2>/dev/null || true
HOOK
chmod +x "${REPO_DIR}/.git/hooks/post-merge"
log "Git hooks installed"

# ─────────────────────────────────────────────
# Python venv
# ─────────────────────────────────────────────

section "Python virtual environment"

if [ ! -d "$VENV_DIR" ]; then
    info "Creating venv at ${VENV_DIR}..."
    sudo -u "${PANEL_USER}" python3 -m venv "$VENV_DIR"
    log "Venv created"
fi

if [ -f "${REPO_DIR}/sensor-daemon/requirements.txt" ]; then
    info "Installing Python dependencies..."
    sudo -u "${PANEL_USER}" "${VENV_DIR}/bin/pip" install --quiet --upgrade pip
    sudo -u "${PANEL_USER}" "${VENV_DIR}/bin/pip" install --quiet \
        -r "${REPO_DIR}/sensor-daemon/requirements.txt"
    log "Python dependencies installed"
else
    warn "sensor-daemon/requirements.txt not found — skipping Python dependencies"
fi

# ─────────────────────────────────────────────
# Systemd services
# ─────────────────────────────────────────────

section "Systemd services"

if [ -f "${REPO_DIR}/system/sensor-daemon.service" ]; then
    info "Installing sensor-daemon service..."
    cp "${REPO_DIR}/system/sensor-daemon.service" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable sensor-daemon
    systemctl start sensor-daemon
    log "sensor-daemon enabled and started"
else
    warn "sensor-daemon.service not found in repo — skipping"
fi

if [ -f "${REPO_DIR}/system/panel-update.service" ] && [ -f "${REPO_DIR}/system/panel-update.timer" ]; then
    info "Installing nightly update timer..."
    cp "${REPO_DIR}/system/panel-update.service" /etc/systemd/system/
    cp "${REPO_DIR}/system/panel-update.timer" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable panel-update.timer
    systemctl start panel-update.timer
    log "Nightly update timer enabled"
else
    warn "panel-update service/timer not found in repo — skipping"
fi

# ─────────────────────────────────────────────
# Bash profile (kiosk startup)
# ─────────────────────────────────────────────

section "Kiosk startup"

BASH_PROFILE="${PANEL_HOME}/.bash_profile"

# Create .bash_profile if it doesn't exist
touch "$BASH_PROFILE"
chown "${PANEL_USER}:${PANEL_USER}" "$BASH_PROFILE"

if ! grep -q "ha-panel" "$BASH_PROFILE"; then
    cat >> "$BASH_PROFILE" << 'EOF'

# HA Panel kiosk — start labwc on TTY1 login
if [ -z "$WAYLAND_DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    exec /opt/ha-panel/repo/system/startup.sh
fi
EOF
    log ".bash_profile updated"
else
    log ".bash_profile already configured"
fi

# ─────────────────────────────────────────────
# Firewall
# ─────────────────────────────────────────────

section "Firewall"

cat > /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        iif lo accept
        ct state established,related accept
        ip saddr 192.168.1.0/24 tcp dport { 22, 9090, 8080 } accept
        ip6 nexthdr icmpv6 accept
        ip protocol icmp accept
        drop
    }
    chain forward {
        type filter hook forward priority 0; policy drop;
    }
    chain output {
        type filter hook output priority 0; policy accept;
    }
}
EOF

systemctl enable nftables
systemctl restart nftables
log "Firewall configured"

# ─────────────────────────────────────────────
# Unattended upgrades (security only)
# ─────────────────────────────────────────────

section "Security updates"

cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

log "Unattended security upgrades enabled"

# ─────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────

section "Installation complete"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  HA Panel installation complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Panel ID:   ${PANEL_ID}"
echo "  User:       ${PANEL_USER}"
echo "  HA server:  ${HA_URL}"
echo "  MQTT:       ${MQTT_HOST}:${MQTT_PORT}"
echo "  Repo:       ${REPO_DIR}"
echo "  Venv:       ${VENV_DIR}"
echo ""
echo "  The panel will start automatically on next reboot."
echo ""
read -rp "  Reboot now? [Y/n] " reboot_now
if [[ ! "$reboot_now" =~ ^[Nn]$ ]]; then
    reboot
fi

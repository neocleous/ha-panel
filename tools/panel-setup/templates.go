package main

const wifiTemplate = `
# ── Wi-Fi ─────────────────────────────────────────────────────────────────────────
log "Configuring Wi-Fi (@SSID@)..."

# Try NetworkManager first (Pi OS Trixie), fall back to wpa_supplicant
if command -v nmcli &>/dev/null && systemctl is-active NetworkManager &>/dev/null; then
    nmcli radio wifi on
    nmcli dev wifi connect "@SSID@" password "@WPASS@" ifname wlan0 2>/dev/null && \
        log "Connected via NetworkManager." || \
        log "NetworkManager connection failed — trying wpa_supplicant."
fi

# wpa_supplicant fallback (Pi OS Lite Bookworm default)
if ! nmcli -t -f STATE general 2>/dev/null | grep -q "connected"; then
    cat > /etc/wpa_supplicant/wpa_supplicant.conf << 'WPAEOF'
country=@WCOUNTRY@
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="@SSID@"
    psk="@WPASS@"
    key_mgmt=WPA-PSK
}
WPAEOF
    chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
    rfkill unblock wifi 2>/dev/null || true
    wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null || true
    sleep 3
    dhclient wlan0 2>/dev/null || true
    log "wpa_supplicant configured."
fi
`

const firstrunTemplate = `#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  HA Panel — First-boot setup
#  Generated @GENERATED@ by Panel Setup
#  ⚠  Contains credentials — self-deletes after running.
#  Log: /boot/firmware/firstrun.log (readable from a computer after boot)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# Log to boot partition so it's readable by inserting SD elsewhere afterwards
LOG=/boot/firmware/firstrun.log
exec > >(tee -a "$LOG") 2>&1

log() { echo "$(date '+%H:%M:%S')  $*"; }

log "═══ HA Panel first-boot setup — @HOSTNAME@ ═════════════════════════════"
log "Generated: @GENERATED@"

PANEL_BASE=/opt/ha-panel
REPO_DIR=$PANEL_BASE/repo
VENV_DIR=$PANEL_BASE/venv

# ── User account ──────────────────────────────────────────────────────────────────
# userconf.txt handles creation via Pi OS mechanism; this is belt-and-suspenders
log "Ensuring user @USERNAME@ exists..."
if ! id "@USERNAME@" &>/dev/null; then
    useradd -m -u 1000 -s /bin/bash "@USERNAME@"
    echo "@USERNAME@:@PWHASH@" | chpasswd -e
    log "User @USERNAME@ created."
else
    log "User @USERNAME@ already exists."
fi

# Add to all required groups
for g in adm dialout cdrom sudo audio video plugdev games users input netdev \
          spi i2c gpio render; do
    getent group "$g" &>/dev/null && usermod -aG "$g" "@USERNAME@" || true
done
log "Group membership configured."

# ── Hostname ─────────────────────────────────────────────────────────────────────
log "Setting hostname to @HOSTNAME@..."
echo "@HOSTNAME@" > /etc/hostname
hostnamectl set-hostname "@HOSTNAME@" 2>/dev/null || true
grep -q "127.0.1.1.*@HOSTNAME@" /etc/hosts || \
    sed -i "s/127\.0\.1\.1.*/127.0.1.1\t@HOSTNAME@/" /etc/hosts 2>/dev/null || \
    echo "127.0.1.1\t@HOSTNAME@" >> /etc/hosts
@WIFIBLOCK@
# ── SSH ───────────────────────────────────────────────────────────────────────────
log "Enabling SSH..."
touch /boot/firmware/ssh 2>/dev/null || true
systemctl enable ssh 2>/dev/null || systemctl enable ssh.service 2>/dev/null || true

# ── Wait for network ──────────────────────────────────────────────────────────────
log "Waiting for network access..."
for i in $(seq 1 90); do
    if curl -sf --max-time 3 https://raw.githubusercontent.com >/dev/null 2>&1; then
        log "Network ready after $((i * 2))s."
        break
    fi
    if [[ $i -eq 90 ]]; then
        log "ERROR: No network after 180s."
        log "  Ethernet: check cable is connected."
        log "  Wi-Fi: check SSID and password in firstrun.sh."
        log "  The log file is at /boot/firmware/firstrun.log"
        exit 1
    fi
    sleep 2
done

# ── Timezone and locale ───────────────────────────────────────────────────────────
log "Setting timezone (@TIMEZONE@) and locale (@LOCALE@)..."
timedatectl set-timezone "@TIMEZONE@" 2>/dev/null || true
locale-gen "@LOCALE@" 2>/dev/null || true
update-locale LANG="@LOCALE@" 2>/dev/null || true

# ── Boot config ───────────────────────────────────────────────────────────────────
log "Configuring boot (display overlay, I2C, Bluetooth off)..."
CONFIG=/boot/firmware/config.txt
grep -q "vc4-kms-dsi-waveshare-panel" "$CONFIG" 2>/dev/null || \
    echo "dtoverlay=vc4-kms-dsi-waveshare-panel,8_0_inch" >> "$CONFIG"
grep -q "dtparam=i2c_arm=on" "$CONFIG" 2>/dev/null || \
    echo "dtparam=i2c_arm=on" >> "$CONFIG"
grep -q "disable-bt" "$CONFIG" 2>/dev/null || \
    echo "dtoverlay=disable-bt" >> "$CONFIG"

# Console rotation to portrait (compositor rotation handled by startup.sh)
CMDLINE=/boot/firmware/cmdline.txt
grep -q "fbcon=rotate:" "$CMDLINE" 2>/dev/null || \
    sed -i 's/$/ fbcon=rotate:3/' "$CMDLINE"

# ── Backlight permissions + log files ─────────────────────────────────────────────────
# screen-sleep.py (runs as @USERNAME@) writes the brightness node directly.
cat > /etc/udev/rules.d/90-backlight.rules << 'UDEVRULE'
SUBSYSTEM=="backlight", ACTION=="add", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"
UDEVRULE
log "Backlight udev rule installed."

# Pre-create log files owned by the panel user (startup/update run unprivileged)
touch /var/log/ha-panel-startup.log /var/log/ha-panel-update.log
chown @USERNAME@:@USERNAME@ /var/log/ha-panel-startup.log /var/log/ha-panel-update.log
log "Log files pre-created."

# ── TTY1 autologin ───────────────────────────────────────────────────────────────
# Direct systemd override — more reliable than raspi-config in firstrun context
log "Configuring TTY1 autologin for @USERNAME@..."
mkdir -p /etc/systemd/system/getty@tty1.service.d/
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << 'AUTOLOGIN'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin @USERNAME@ --noclear %I $TERM
AUTOLOGIN

# ── Packages ─────────────────────────────────────────────────────────────────────
log "Installing packages (5–10 minutes on first boot)..."
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
    labwc squeekboard wlr-randr chromium xdg-utils \
    network-manager curl wget \
    python3-smbus2 i2c-tools python3-lgpio python3-evdev \
    python3 python3-pip python3-venv python3-full \
    git unattended-upgrades apt-listchanges nftables \
    raspi-config rpi-eeprom
log "Packages installed."

# ── Clone repo ────────────────────────────────────────────────────────────────────
log "Cloning repo (@REPOURL@)..."
mkdir -p "$PANEL_BASE"
git clone --quiet "@REPOURL@" "$REPO_DIR"
chown -R "@USERNAME@:@USERNAME@" "$PANEL_BASE"
log "Repo ready."

# ── Python venv ───────────────────────────────────────────────────────────────────
# --system-site-packages is required: lgpio is only available as a system package
log "Creating Python venv..."
python3 -m venv --system-site-packages "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade --quiet pip
"$VENV_DIR/bin/pip" install --quiet -r "$REPO_DIR/sensor-daemon/requirements.txt"
log "Venv ready."

# ── Config files ──────────────────────────────────────────────────────────────────
# Canonical sensor-config.py lives OUTSIDE the repo so git reset never wipes it.
# The in-repo path is a symlink.
log "Writing config files..."

# /opt/ha-panel/config — sourced by startup.sh and update.sh
cat > "$PANEL_BASE/config" << 'SHELLCONFIG'
# HA Panel runtime configuration — generated by Panel Setup
PANEL_ID=@HOSTNAME_SH@
HA_URL=@HAURL_SH@
MQTT_HOST=@MQTTHOST_SH@
MQTT_PORT=@MQTTPORT_SH@
MQTT_USER=@MQTTUSER_SH@
MQTT_PASS=@MQTTPASS_SH@
BACKLIGHT_PATH='/sys/class/backlight/11-0045/brightness'
ROTATION=90
SHELLCONFIG
chmod 600 "$PANEL_BASE/config"

# /opt/ha-panel/sensor-config.py — canonical location, outside repo
cat > "$PANEL_BASE/sensor-config.py" << 'PYCONFIG'
# Sensor daemon configuration - generated by Panel Setup
# Canonical location: /opt/ha-panel/sensor-config.py
# Symlinked at:       sensor-daemon/config.py
# Never overwritten by git operations.

PANEL_ID = "@HOSTNAME@"

# MQTT
MQTT_BROKER   = "@MQTTHOST_PY@"
MQTT_PORT     = @MQTTPORT@
MQTT_USERNAME = "@MQTTUSER_PY@"
MQTT_PASSWORD = "@MQTTPASS_PY@"
MQTT_TOPIC_ROOT = f"home/{PANEL_ID}"

# I2C (bus 1 only - bus 0 does not exist on Pi 5)
I2C_BUS = 1

# Polling intervals in seconds
POLL_INTERVAL_TOUCH = 0.1       # AT42QT1070 - 100ms
POLL_INTERVAL_PROXIMITY = 0.2   # VL53L0X - 200ms
POLL_INTERVAL_LIGHT = 10        # VEML6030 - 10s
POLL_INTERVAL_ENV = 30          # BME680 - 30s

# Screen wake
PROXIMITY_WAKE_THRESHOLD_MM = 120   # 12cm
SCREEN_TIMEOUT = 60                 # seconds until screen off

# Backlight
BACKLIGHT_PATH = "/sys/class/backlight/11-0045/brightness"
BACKLIGHT_MAX = 255
BACKLIGHT_ON = 255
BACKLIGHT_OFF = 0

# Calibration offsets - adjust after burn-in if needed
TEMPERATURE_OFFSET = 0.0   # degrees C
HUMIDITY_OFFSET    = 0.0   # percent RH
PYCONFIG
chmod 600 "$PANEL_BASE/sensor-config.py"

# Symlink into repo (protected from git reset --hard)
rm -f "$REPO_DIR/sensor-daemon/config.py"
ln -s "$PANEL_BASE/sensor-config.py" "$REPO_DIR/sensor-daemon/config.py"
log "Config files written and symlinked."

# ── Systemd services ──────────────────────────────────────────────────────────────
log "Installing systemd services..."
cp "$REPO_DIR/system/sensor-daemon.service"  /etc/systemd/system/
cp "$REPO_DIR/system/panel-update.service"   /etc/systemd/system/
cp "$REPO_DIR/system/panel-update.timer"     /etc/systemd/system/
systemctl daemon-reload
systemctl enable sensor-daemon
systemctl enable panel-update.timer
log "Services installed."

# ── Kiosk autostart ───────────────────────────────────────────────────────────────
log "Writing kiosk autostart (~/.bash_profile)..."
BASH_PROFILE="/home/@USERNAME@/.bash_profile"
cat >> "$BASH_PROFILE" << 'BPEOF'
# ── HA Panel kiosk startup ───────────────────────────────────────────────────────
if [[ -z "${WAYLAND_DISPLAY:-}" && "$(tty)" == '/dev/tty1' ]]; then
  exec bash /opt/ha-panel/repo/system/startup.sh
fi
BPEOF
chown "@USERNAME@:@USERNAME@" "$BASH_PROFILE"

# ── Firewall ─────────────────────────────────────────────────────────────────────
log "Configuring firewall (SSH from @SUBNET@ only)..."
cat > /etc/nftables.conf << 'NFTEOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    iif lo accept
    ct state established,related accept
    ip  protocol icmp   accept
    ip6 nexthdr  icmpv6 accept
    ip saddr @SUBNET@ tcp dport 22 accept
    drop
  }
  chain forward { type filter hook forward priority 0; policy drop; }
  chain output  { type filter hook output  priority 0; policy accept; }
}
NFTEOF
systemctl enable nftables

# ── Unattended upgrades ───────────────────────────────────────────────────────────
cat > /etc/apt/apt.conf.d/20ha-panel-upgrades << 'APTEOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "0";
APTEOF

# ── Done ────────────────────────────────────────────────────────────────────────
log "═══ First-boot setup complete ══════════════════════════════════════"
log "  Panel ID : @HOSTNAME@"
log "  HA URL   : @HAURL@"
log "  MQTT     : @MQTTHOST@:@MQTTPORT@"
log ""
log "  Rebooting in 5 seconds — panel will load HA dashboard automatically."
log "  If anything went wrong, this log is at /boot/firmware/firstrun.log"

# Self-delete — file contained credentials and is no longer needed
rm -f /boot/firmware/firstrun.sh

sleep 5
reboot
`

const page = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>HA Panel Setup</title>
<style>
  :root{color-scheme:light dark}
  body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:640px;margin:2rem auto;
       padding:0 1.25rem;background:Canvas;color:CanvasText}
  h1{font-size:1.35rem;margin:0 0 .25rem} .sub{color:gray;margin:0 0 1.5rem;font-size:.9rem}
  fieldset{border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:10px;
           margin:0 0 1.1rem;padding:.9rem 1.1rem 1.1rem}
  legend{font-weight:600;font-size:.95rem;padding:0 .4rem}
  label{display:block;font-size:.8rem;color:gray;margin:.65rem 0 .2rem}
  input,select{width:100%;box-sizing:border-box;font-size:.95rem;padding:.45rem .6rem;
        border:1px solid color-mix(in srgb,CanvasText 25%,transparent);border-radius:7px;
        background:Field;color:FieldText}
  select{height:2.15rem}
  .row{display:flex;gap:.8rem} .row>div{flex:1}
  .hint{font-size:.78rem;color:gray;margin-top:.25rem}
  .pill{display:inline-block;font-size:.78rem;padding:.15rem .55rem;border-radius:99px;margin:.15rem .2rem 0 0;
        background:color-mix(in srgb,CanvasText 8%,transparent)}
  .ok{color:#188038}.bad{color:#d93025}.warn{color:#b06000}
  button{font-size:.95rem;padding:.55rem 1.1rem;border-radius:8px;border:1px solid
         color-mix(in srgb,CanvasText 25%,transparent);background:Field;color:FieldText;cursor:pointer}
  button.primary{background:#2f6fdd;border-color:#2f6fdd;color:#fff}
  button:disabled{opacity:.45;cursor:default}
  .actions{display:flex;gap:.8rem;align-items:center;margin:1.4rem 0}
  #sdstate{font-size:.85rem}
  #result{display:none}
  #result ol{line-height:1.7}
  .banner{border-radius:10px;padding:.8rem 1rem;margin:0 0 1.2rem;font-size:.9rem;
          background:color-mix(in srgb,CanvasText 6%,transparent)}
</style></head><body>
<h1>HA Panel setup</h1>
<p class="sub">Generates and writes the SD-card first-boot files</p>
<div id="app">
<div class="banner" id="scan">Scanning network for existing panels…</div>
<fieldset><legend>Panel</legend>
  <div class="row">
    <div><label>Panel number</label><input id="panel_num" type="number" min="1" max="99"></div>
    <div><label>Hostname</label><input id="hostname" readonly></div>
  </div>
  <div class="row">
    <div><label>Pi username</label><input id="username"></div>
    <div><label>Pi user password</label><input id="pi_pass" type="password" autocomplete="new-password"></div>
  </div>
</fieldset>
<fieldset><legend>Home Assistant</legend>
  <label>HA base URL</label><input id="ha_base">
  <label>Dashboard URL for this panel</label><input id="ha_url">
  <div class="hint">Create the dashboard with this url_path in HA before first boot</div>
</fieldset>
<fieldset><legend>MQTT broker</legend>
  <div class="row">
    <div><label>Host / IP</label><input id="mqtt_host"></div>
    <div style="max-width:110px"><label>Port</label><input id="mqtt_port"></div>
  </div>
  <div class="row">
    <div><label>Username</label><input id="mqtt_user"></div>
    <div><label>Password</label><input id="mqtt_pass" type="password" autocomplete="new-password"></div>
  </div>
  <div class="actions" style="margin:0.9rem 0 0">
    <button id="testmqtt">Test connection</button><span id="mqttstate"></span>
  </div>
</fieldset>
<fieldset><legend>Wi-Fi (leave SSID empty for ethernet)</legend>
  <div class="row">
    <div><label>SSID</label><input id="wifi_ssid"></div>
    <div><label>Password</label><input id="wifi_pass" type="password"></div>
    <div style="max-width:230px"><label>Country (Wi-Fi regulatory)</label>
      <select id="wifi_country">__COUNTRY_OPTIONS__</select></div>
  </div>
</fieldset>
<div class="actions">
  <button class="primary" id="write" disabled>Write to SD card</button>
  <span id="sdstate"></span>
</div>
</div>
<div id="result">
  <div class="banner ok" style="font-weight:600">Files written to the SD card</div>
  <ol>
    <li>Eject the SD card and insert it into the panel</li>
    <li>Power on — setup runs unattended for about 10 minutes, then the panel reboots into the dashboard</li>
    <li>If anything goes wrong: reinsert the SD in this computer and read <code>firstrun.log</code> on it</li>
    <li>In Home Assistant: clone the touch-button automation for the new panel's buttons</li>
  </ol>
  <div class="hint">No credential files were left on this computer.</div>
  <div class="actions"><button onclick="location.reload()">Prepare another panel</button>
  <button id="quit2">Quit</button></div>
</div>
<script>
const $=id=>document.getElementById(id);
let mqttOK=false;
function fld(){return{panel_num:$('panel_num').value,hostname:$('hostname').value,
 username:$('username').value,pi_pass:$('pi_pass').value,ha_base:$('ha_base').value,
 ha_url:$('ha_url').value,mqtt_host:$('mqtt_host').value,mqtt_port:$('mqtt_port').value,
 mqtt_user:$('mqtt_user').value,mqtt_pass:$('mqtt_pass').value,wifi_ssid:$('wifi_ssid').value,
 wifi_pass:$('wifi_pass').value,wifi_country:$('wifi_country').value,
 timezone:'Europe/Zurich',locale:'en_GB.UTF-8',
 repo_url:'https://github.com/neocleous/ha-panel.git'}}
function syncNames(){
 const n=String($('panel_num').value||'1').padStart(2,'0');
 $('hostname').value='panel-'+n;
 const base=$('ha_base').value.replace(/\/+$/,'');
 $('ha_url').value=base+'/panel-'+n+'/0';
}
async function init(){
 const d=await (await fetch('/api/defaults')).json();
 for(const k of['username','ha_base','mqtt_port','mqtt_user','wifi_ssid'])$(k).value=d.prefs[k]??'';
 $('wifi_country').value=d.prefs.wifi_country||'CH';
 $('panel_num').value=d.next_panel;
 $('mqtt_host').value=d.mqtt_host_guess||'';
 syncNames();
 $('scan').innerHTML= d.existing.length
  ? 'Existing panels found: '+d.existing.map(n=>'<span class="pill">panel-'+String(n).padStart(2,'0')+'</span>').join('')
    +' — next free number pre-selected'
  : 'No existing panels detected on the network';
 pollSD();setInterval(pollSD,2000);
}
async function pollSD(){
 const s=await (await fetch('/api/bootfs')).json();
 if(s.path){$('sdstate').innerHTML='<span class="ok">SD card detected: '+s.path+'</span>';}
 else{$('sdstate').innerHTML='<span class="warn">Insert a freshly flashed Pi OS Lite SD card (bootfs)</span>';}
 gate(s.path);
}
function gate(sd){
 const f=fld();
 const ready=sd&&mqttOK&&f.pi_pass&&f.mqtt_pass&&(!f.wifi_ssid||f.wifi_pass);
 $('write').disabled=!ready;
}
$('panel_num').addEventListener('input',syncNames);
$('ha_base').addEventListener('input',syncNames);
document.addEventListener('input',()=>{mqttOK=false;$('mqttstate').textContent='';pollSD();});
$('testmqtt').onclick=async()=>{
 $('mqttstate').textContent='Testing…';
 const r=await(await fetch('/api/mqtt',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify(fld())})).json();
 mqttOK=r.ok;
 $('mqttstate').innerHTML=r.ok?'<span class="ok">Broker reachable, credentials accepted</span>'
   :'<span class="bad">'+r.error+'</span>';
 pollSD();
};
$('write').onclick=async()=>{
 $('write').disabled=true;$('write').textContent='Writing…';
 const r=await(await fetch('/api/write',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify(fld())})).json();
 if(r.ok){$('app').style.display='none';$('result').style.display='block';}
 else{alert(r.error);$('write').textContent='Write to SD card';pollSD();}
};
$('quit2').onclick=()=>{fetch('/api/quit',{method:'POST'});window.close();};
init();
</script></body></html>`

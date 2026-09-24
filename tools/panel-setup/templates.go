package main

// wifiTemplate is part 1's Wi-Fi step: a NetworkManager keyfile (Pi OS Bookworm
// and later), read by NetworkManager when it starts on the next boot. The key is
// the WPA2 PSK Panel Setup derived from the passphrase (wpaPSK), so no passphrase
// is ever escaped into the file. The regulatory country goes onto cmdline.txt —
// until it is set, Pi OS keeps the radio blocked.
const wifiTemplate = `install -d -m 700 /etc/NetworkManager/system-connections
cat > /etc/NetworkManager/system-connections/panel-wifi.nmconnection <<'NMCONN'
[connection]
id=panel-wifi
uuid=@UUID@
type=wifi
autoconnect=true
interface-name=wlan0

[wifi]
mode=infrastructure
ssid=@SSID_NM@

[wifi-security]
key-mgmt=wpa-psk
psk=@PSK@

[ipv4]
method=auto

[ipv6]
addr-gen-mode=default
method=auto
NMCONN
chmod 600 /etc/NetworkManager/system-connections/panel-wifi.nmconnection
if command -v raspi-config >/dev/null 2>&1; then
  raspi-config nonint do_wifi_country @COUNTRY@ || true
fi
grep -q "cfg80211.ieee80211_regdom=" "$FW/cmdline.txt" || sed -i 's/$/ cfg80211.ieee80211_regdom=@COUNTRY@/' "$FW/cmdline.txt"
rfkill unblock wifi 2>/dev/null || true
for f in /var/lib/systemd/rfkill/*:wlan; do if [ -e "$f" ]; then echo 0 > "$f"; fi; done
log "Wi-Fi: panel-wifi.nmconnection, country @COUNTRY@"
`

// firstrunTemplate is part 1 of the first boot. cmdline.txt's systemd.run=
// runs it once, under kernel-command-line.target: early, before NetworkManager,
// with no network. So it does nothing that needs one — it writes this panel's
// own files and arms part 2 for the next boot. It must never exit non-zero: a
// failed systemd.run= command ends that boot (on Pi OS 2026-09-15 the Pi powers
// off) with the hook still in cmdline.txt — so it repeats on every power-up.
const firstrunTemplate = `#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  HA Panel — first boot, part 1 of 2 — generated @GENERATED@ by Panel Setup
#  Run ONCE by cmdline.txt's systemd.run=, early and with NO network. Writes this
#  panel's own files and arms part 2 (panel-firstboot.service), which runs on the
#  next boot with the network up: clone, install.sh --unattended, reboot.
#  ⚠  Contains credentials: removes itself, userconf.txt and its words in
#     cmdline.txt before it ends.
#  Log: firstrun.log on the boot partition — never contains a secret.
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail   # no -e: this must always reach its end (see the last step)
FW=/boot/firmware
[ -d "$FW" ] || FW=/boot
exec >>"$FW/firstrun.log" 2>&1
log()  { echo "$(date '+%H:%M:%S')  $*"; }
FAILED=0
fail() { log "ERROR: $*"; FAILED=1; }
IC=/usr/lib/raspberrypi-sys-mods/imager_custom
PANEL_USER=@USERNAME_SH@
PANEL_HOSTNAME=@HOSTNAME_SH@
# shellcheck disable=SC2016  # a $6$ hash, single-quoted on purpose
PWHASH=@PWHASH_SH@
log "═══ HA Panel first boot, part 1 — @HOSTNAME@ (generated @GENERATED@)"

# ── 1. User ──────────────────────────────────────────────────────────────────────
# Pi OS ships a disabled first user at uid 1000 ('pi'); userconf-pi renames it,
# sets the password and shell, and retires its own first-boot service — exactly
# what Raspberry Pi Imager's firstrun does.
if [ -x /usr/lib/userconf-pi/userconf ]; then
  if /usr/lib/userconf-pi/userconf "$PANEL_USER" "$PWHASH"; then
    rm -f "$FW/userconf.txt"   # consumed; on failure it stays for userconfig.service
  else
    fail "userconf — userconf.txt left for Pi OS to apply on the next boot"
  fi
else
  id "$PANEL_USER" >/dev/null 2>&1 || useradd -m -s /bin/bash "$PANEL_USER" || fail "useradd"
  echo "$PANEL_USER:$PWHASH" | chpasswd -e || fail "chpasswd"
  rm -f "$FW/userconf.txt"
fi
for g in adm dialout cdrom sudo audio video plugdev games users input netdev \
         spi i2c gpio render; do
  if getent group "$g" >/dev/null; then usermod -aG "$g" "$PANEL_USER"; fi
done
log "User: $PANEL_USER"

# ── 2. Hostname ──────────────────────────────────────────────────────────────────
if [ -x "$IC" ]; then
  "$IC" set_hostname "$PANEL_HOSTNAME" || fail "hostname"
else
  CUR="$(tr -d ' \t\n\r' < /etc/hostname)"
  echo "$PANEL_HOSTNAME" > /etc/hostname
  sed -i "s/127\.0\.1\.1.*$CUR/127.0.1.1\t$PANEL_HOSTNAME/g" /etc/hosts
fi
log "Hostname: $PANEL_HOSTNAME"

# ── 3. SSH ───────────────────────────────────────────────────────────────────────
if [ -x "$IC" ]; then "$IC" enable_ssh || fail "ssh"; else systemctl enable ssh >/dev/null 2>&1 || fail "ssh"; fi
log "SSH: enabled"

# ── 4. Wi-Fi ─────────────────────────────────────────────────────────────────────
@WIFIBLOCK@
# ── 5. Timezone and locale ───────────────────────────────────────────────────────
if [ -x "$IC" ]; then
  "$IC" set_timezone @TIMEZONE@ || fail "timezone"
else
  { ln -sf /usr/share/zoneinfo/@TIMEZONE@ /etc/localtime && echo @TIMEZONE@ > /etc/timezone; } || fail "timezone"
fi
if ! grep -qx 'LANG=@LOCALE@' /etc/default/locale 2>/dev/null; then
  sed -i '/^# *@LOCALE@ UTF-8/s/^# *//' /etc/locale.gen
  { locale-gen >/dev/null && update-locale LANG=@LOCALE@; } || fail "locale"
fi
log "Timezone: @TIMEZONE@, locale: @LOCALE@"

# ── 6. This panel's own files ────────────────────────────────────────────────────
# Outside the repo, so the nightly git reset --hard never touches them; mode 600.
# install.sh (part 2) symlinks sensor-config.py into the repo.
install -d -m 755 /opt/ha-panel
cat > /opt/ha-panel/config << 'SHELLCONFIG'
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

cat > /opt/ha-panel/sensor-config.py << 'PYCONFIG'
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
chown "$PANEL_USER:$PANEL_USER" /opt/ha-panel /opt/ha-panel/config /opt/ha-panel/sensor-config.py || fail "chown /opt/ha-panel"
chmod 600 /opt/ha-panel/config /opt/ha-panel/sensor-config.py
log "Config: /opt/ha-panel/config and sensor-config.py (mode 600)"

# ── 7. Arm part 2 for the next boot ──────────────────────────────────────────────
cat > /opt/ha-panel/firstboot.sh << 'FIRSTBOOT'
@FIRSTBOOT@FIRSTBOOT
chmod 700 /opt/ha-panel/firstboot.sh
cat > /etc/systemd/system/panel-firstboot.service << 'UNIT'
@FIRSTBOOT_UNIT@UNIT
ln -sf /etc/systemd/system/panel-firstboot.service \
       /etc/systemd/system/multi-user.target.wants/panel-firstboot.service
log "Part 2 armed: panel-firstboot.service"

# ── 8. Disarm part 1 ─────────────────────────────────────────────────────────────
# Exactly the three hook words go — anything appended after them (the Wi-Fi
# regulatory domain) stays. Then this file, which holds credentials.
sed -i -E 's# systemd\.run=[^ ]+##; s# systemd\.run_success_action=[^ ]+##; s# systemd\.unit=kernel-command-line\.target##' "$FW/cmdline.txt"
rm -f "$FW/firstrun.sh"
if [ "$FAILED" = 0 ]; then
  log "═══ Part 1 done — rebooting. Part 2 installs everything and logs to firstboot.log"
else
  log "═══ Part 1 finished WITH ERRORS (above) — rebooting anyway. Part 2 logs to firstboot.log"
fi
sync
exit 0   # systemd.run_success_action=reboot takes it from here
`

// firstbootScript is part 2, written to /opt/ha-panel/firstboot.sh by part 1
// and run by panel-firstboot.service on the next boot, after
// network-online.target. The install logic lives in system/install.sh on main —
// one installer for both routes; this only fetches it and runs it. A failure
// leaves it armed, and the next boot tries again.
const firstbootScript = `#!/bin/bash
# HA Panel — first boot, part 2 of 2 (written by part 1). With the network up:
# clone the repo, run system/install.sh --unattended, reboot into the kiosk.
# On a failure it stays armed and runs again at the next boot.
# Logs: firstboot.log on the boot partition, and /var/log/ha-panel-firstboot.log.
set -uo pipefail
FW=/boot/firmware
[ -d "$FW" ] || FW=/boot
exec > >(tee -a "$FW/firstboot.log" /var/log/ha-panel-firstboot.log) 2>&1
log() { echo "$(date '+%H:%M:%S')  $*"; }
PANEL_USER=@USERNAME_SH@
REPO_URL=@REPOURL_SH@
REPO_DIR=/opt/ha-panel/repo
# scheme://host[:port] of the repo — any HTTP answer from it means the network is up
ORIGIN="$(printf '%s' "$REPO_URL" | sed -E 's#^([a-z]+://)([^/@]*@)?([^/]+).*#\1\3#')"
log "═══ HA Panel first boot, part 2 — $REPO_URL"

up=""
deadline=$((SECONDS + 300))
while [ "$SECONDS" -lt "$deadline" ]; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$ORIGIN/" || true)"
  if [ -n "$code" ] && [ "$code" != 000 ]; then up=1; break; fi
  sleep 2
done
if [ -z "$up" ]; then
  log "ERROR: no network after 300 s — check the Ethernet cable, or the Wi-Fi name, password and country"
  log "Part 2 stays armed and runs again at the next boot"
  exit 1
fi
log "Network: up after ${SECONDS} s"

# Pi OS Lite ships without git
if ! command -v git >/dev/null 2>&1; then
  log "Installing git"
  if ! { DEBIAN_FRONTEND=noninteractive apt-get update -q >/dev/null &&
         DEBIAN_FRONTEND=noninteractive apt-get install -y -q git >/dev/null; }; then
    log "ERROR: git could not be installed — part 2 stays armed"
    exit 1
  fi
fi
if [ ! -d "$REPO_DIR/.git" ]; then
  rm -rf "$REPO_DIR"
  if ! git clone --quiet "$REPO_URL" "$REPO_DIR"; then
    log "ERROR: clone of $REPO_URL failed — part 2 stays armed"
    exit 1
  fi
fi
log "Repo: $REPO_DIR at $(git -c safe.directory="$REPO_DIR" -C "$REPO_DIR" rev-parse --short HEAD)"

log "Running install.sh --unattended (packages, services, kiosk) — 5 to 15 minutes"
if ! bash "$REPO_DIR/system/install.sh" --unattended --user "$PANEL_USER"; then
  log "ERROR: install.sh failed — /var/log/ha-panel-install.log; part 2 stays armed"
  exit 1
fi

systemctl disable panel-firstboot.service >/dev/null 2>&1 ||
  rm -f /etc/systemd/system/multi-user.target.wants/panel-firstboot.service
rm -f /opt/ha-panel/firstboot.sh
log "═══ Installed — rebooting into the kiosk"
sync
systemctl --no-block reboot
`

// firstbootUnit runs part 2. Before getty@tty1 so the panel's screen shows the
// install's progress rather than a login prompt; journal+console puts it there.
const firstbootUnit = `[Unit]
Description=HA Panel first boot, part 2: clone, install.sh --unattended, reboot into the kiosk
Wants=network-online.target
After=network-online.target
Before=getty@tty1.service
ConditionPathExists=/opt/ha-panel/firstboot.sh

[Service]
Type=oneshot
ExecStart=/usr/bin/bash /opt/ha-panel/firstboot.sh
StandardOutput=journal+console
StandardError=journal+console
TimeoutStartSec=3600

[Install]
WantedBy=multi-user.target
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
    <li>Power on. Part 1 takes about a minute and reboots; part 2 installs everything (about 10 minutes on a Pi 5, progress on the screen) and reboots into the dashboard</li>
    <li>If anything goes wrong: reinsert the SD in this computer and read <code>firstrun.log</code> and <code>firstboot.log</code> on it</li>
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

#!/usr/bin/env python3
"""
HA Panel provisioning server
Serves the provisioning UI on port 8080.
Handles Wi-Fi connection and panel configuration.

Endpoints:
  GET  /              → index.html  (Wi-Fi network list)
  GET  /password.html → password.html
  GET  /configure.html→ configure.html
  GET  /scan          → JSON list of Wi-Fi networks
  GET  /status        → JSON: {connected, ip, config_exists}
  GET  /panel-info    → JSON: {hostname, gateway, ip}
  POST /resolve     → Resolve hostname to IP  {host}
  POST /connect       → Connect to Wi-Fi  {ssid, password}
  POST /configure     → Write config files + reboot
"""

import json
import socket
import logging
import os
import re
import subprocess
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

PANEL_BASE         = Path("/opt/ha-panel")
CONFIG_FILE        = PANEL_BASE / "config"           # shell format, sourced by startup.sh
SENSOR_CONFIG_CANON= PANEL_BASE / "sensor-config.py" # canonical — lives OUTSIDE repo
REPO_DIR           = PANEL_BASE / "repo"
SENSOR_CONFIG_LINK = REPO_DIR / "sensor-daemon" / "config.py"  # symlink into repo
UI_DIR             = Path(__file__).parent
PORT               = 8080

# ── Logging ────────────────────────────────────────────────────────────────────
# Minimal logging — never log passwords
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("provisioning")

# ── Helper ─────────────────────────────────────────────────────────────────────

def run(cmd, timeout=15, check=False):
    """Run a shell command, return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


def detect_backlight_path():
    """Return the sysfs brightness path for the first detected backlight."""
    bl = Path("/sys/class/backlight")
    if bl.exists():
        for entry in sorted(bl.iterdir()):
            brightness = entry / "brightness"
            if brightness.exists():
                log.info(f"Detected backlight: {brightness}")
                return str(brightness)
    # Known path for Waveshare 8" DSI on Pi 5
    return "/sys/class/backlight/11-0045/brightness"


def get_default_gateway():
    """Return the default gateway IP, or empty string."""
    _, out, _ = run(["ip", "route", "show", "default"])
    for line in out.splitlines():
        if "default" in line:
            parts = line.split()
            if "via" in parts:
                idx = parts.index("via")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
    return ""


def get_local_ip():
    """Return the first non-loopback IP address."""
    _, out, _ = run(["hostname", "-I"])
    ips = out.strip().split()
    return ips[0] if ips else ""


def is_network_connected():
    """Return True if nmcli reports connectivity."""
    _, out, _ = run(["nmcli", "-t", "-f", "STATE,CONNECTIVITY", "general"], timeout=5)
    return "connected" in out.lower()


# ── Request handler ────────────────────────────────────────────────────────────

class ProvisioningHandler(BaseHTTPRequestHandler):

    # Suppress default access log lines to avoid leaking credentials
    def log_message(self, fmt, *args):
        if "configure" not in (args[0] if args else ""):
            log.info(f"{self.client_address[0]} {fmt % args}")

    # ── Helpers ─────────────────────────────────────────────────────────────

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, fpath, content_type="text/html; charset=utf-8"):
        p = Path(fpath)
        if not p.exists():
            self.send_response(404)
            self.end_headers()
            return
        body = p.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    # ── Routing ─────────────────────────────────────────────────────────────

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        routes = {
            "/":                 lambda: self.send_file(UI_DIR / "index.html"),
            "/index.html":       lambda: self.send_file(UI_DIR / "index.html"),
            "/password.html":    lambda: self.send_file(UI_DIR / "password.html"),
            "/configure.html":   lambda: self.send_file(UI_DIR / "configure.html"),
            "/scan":             self.handle_scan,
            "/status":           self.handle_status,
            "/panel-info":       self.handle_panel_info,
        }

        handler = routes.get(path)
        if handler:
            handler()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/resolve":
            self.handle_resolve()
        elif path == "/connect":
            self.handle_connect()
        elif path == "/configure":
            self.handle_configure()
        else:
            self.send_response(404)
            self.end_headers()

    # ── GET handlers ────────────────────────────────────────────────────────

    def handle_scan(self):
        """Scan for Wi-Fi networks via nmcli."""
        rc, out, err = run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi", "list", "--rescan", "yes"],
            timeout=20
        )
        networks = []
        seen = set()
        for line in out.strip().splitlines():
            # nmcli -t uses : as separator; escape : in SSID with \:
            parts = re.split(r"(?<!\\):", line)
            if len(parts) < 2:
                continue
            ssid     = parts[0].replace("\\:", ":").strip()
            signal   = parts[1].strip()
            security = parts[2].strip() if len(parts) > 2 else ""

            if not ssid or ssid in seen:
                continue
            seen.add(ssid)
            networks.append({
                "ssid":    ssid,
                "signal":  int(signal) if signal.isdigit() else 0,
                "secured": bool(security and security not in ("--", "")),
            })

        networks.sort(key=lambda x: x["signal"], reverse=True)
        self.send_json({"networks": networks[:20]})

    def handle_status(self):
        """Return current network state."""
        self.send_json({
            "connected":     is_network_connected(),
            "ip":            get_local_ip(),
            "config_exists": CONFIG_FILE.exists(),
        })

    def handle_panel_info(self):
        """Return hostname + gateway for pre-filling the setup wizard."""
        _, hostname, _ = run(["hostname"])
        hostname = hostname.strip() or "panel-01"
        gateway  = get_default_gateway()
        ip       = get_local_ip()
        self.send_json({
            "hostname": hostname,
            "gateway":  gateway,
            "ip":       ip,
        })

    # ── POST handlers ────────────────────────────────────────────────────────

    def handle_resolve(self):
        """
        Resolve a hostname to an IPv4 address.
        Returns the IP unchanged if the input is already an IP address.
        Used by the setup wizard to convert homeassistant.local → 192.168.x.x
        so MQTT config always contains a raw IP rather than an mDNS hostname.
        """
        try:
            data = self.read_json()
            host = data.get("host", "").strip()

            if not host:
                self.send_json({"success": False, "error": "No host provided"}, 400)
                return

            # getaddrinfo works for both hostnames and IPs; AF_INET = IPv4 only
            results = socket.getaddrinfo(host, None, socket.AF_INET)
            if not results:
                self.send_json({"success": False, "error": f"Could not resolve {host}"})
                return

            ip = results[0][4][0]
            log.info(f"Resolved {host} → {ip}")
            self.send_json({"success": True, "host": host, "ip": ip})

        except socket.gaierror as e:
            log.warning(f"DNS resolution failed for {data.get('host', '?')}: {e}")
            self.send_json({"success": False, "error": f"Could not resolve hostname"})
        except Exception as e:
            log.error(f"handle_resolve error: {e}")
            self.send_json({"success": False, "error": "Internal error"}, 500)

    def handle_connect(self):
        """Connect to a Wi-Fi network via nmcli."""
        try:
            data     = self.read_json()
            ssid     = data.get("ssid", "").strip()
            password = data.get("password", "")

            if not ssid:
                self.send_json({"success": False, "error": "SSID is required"}, 400)
                return

            cmd = ["nmcli", "dev", "wifi", "connect", ssid]
            if password:
                cmd += ["password", password]

            log.info(f"Connecting to SSID: {ssid}")
            rc, out, err = run(cmd, timeout=30)

            if rc != 0:
                self.send_json({"success": False, "error": "Connection failed"})
                return

            # Give the connection a moment to establish
            time.sleep(2)
            connected = is_network_connected()
            self.send_json({"success": connected})

        except Exception as e:
            log.error(f"handle_connect error: {e}")
            self.send_json({"success": False, "error": "Internal error"}, 500)

    def handle_configure(self):
        """
        Write /opt/ha-panel/config and /opt/ha-panel/sensor-config.py,
        symlink sensor-config.py into the repo, then schedule a reboot.
        """
        try:
            data = self.read_json()

            panel_id  = data.get("panel_id",  "panel-01").strip()
            ha_url    = data.get("ha_url",    "").strip().rstrip("/")
            mqtt_host = data.get("mqtt_host", "").strip()
            mqtt_port = data.get("mqtt_port", "1883").strip()
            mqtt_user = data.get("mqtt_user", "").strip()
            mqtt_pass = data.get("mqtt_pass", "")

            # Validate required fields (never log mqtt_pass)
            if not all([ha_url, mqtt_host, mqtt_port, mqtt_user, mqtt_pass]):
                self.send_json({"success": False, "error": "All fields are required"}, 400)
                return

            if not ha_url.startswith("http"):
                self.send_json({"success": False, "error": "HA URL must start with http"}, 400)
                return

            if not re.match(r"^\d+$", mqtt_port) or not (1 <= int(mqtt_port) <= 65535):
                self.send_json({"success": False, "error": "MQTT port must be a number between 1 and 65535"}, 400)
                return

            if not re.match(r"^[a-z0-9-]+$", panel_id):
                self.send_json({"success": False, "error": "Panel ID must be lowercase letters, numbers and hyphens"}, 400)
                return

            log.info(f"Writing config: panel_id={panel_id} ha_url={ha_url} mqtt_host={mqtt_host} port={mqtt_port} user={mqtt_user}")

            backlight_path = detect_backlight_path()

            # ── 1. /opt/ha-panel/config (shell format) ──────────────────────
            PANEL_BASE.mkdir(parents=True, exist_ok=True)

            shell_config = (
                "# HA Panel runtime configuration\n"
                "# Generated by provisioning — use setup.sh to reconfigure\n"
                "#\n"
                f"PANEL_ID={panel_id}\n"
                f"HA_URL={ha_url}\n"
                f"MQTT_HOST={mqtt_host}\n"
                f"MQTT_PORT={mqtt_port}\n"
                f"MQTT_USER={mqtt_user}\n"
                f"MQTT_PASS={mqtt_pass}\n"
                f"BACKLIGHT_PATH={backlight_path}\n"
            )
            CONFIG_FILE.write_text(shell_config)
            os.chmod(CONFIG_FILE, 0o600)

            # ── 2. /opt/ha-panel/sensor-config.py (canonical, outside repo) ─
            py_config = (
                "# Sensor daemon configuration\n"
                "# Generated by provisioning — use setup.sh to reconfigure\n"
                "# Canonical location: /opt/ha-panel/sensor-config.py\n"
                "# Linked into repo at: sensor-daemon/config.py\n"
                "# This file must NEVER be overwritten by git operations.\n"
                "#\n"
                f'PANEL_ID = "{panel_id}"\n'
                "\n"
                "# MQTT\n"
                f'MQTT_BROKER   = "{mqtt_host}"\n'
                f'MQTT_PORT     = {mqtt_port}\n'
                f'MQTT_USERNAME = "{mqtt_user}"\n'
                f'MQTT_PASSWORD = "{mqtt_pass}"\n'
                "\n"
                "# I2C bus\n"
                "I2C_BUS = 1\n"
                "\n"
                "# Sensor I2C addresses (do not change unless you know why)\n"
                "BME680_I2C_ADDR  = 0x77  # SDO pulled high on this breakout\n"
                "VEML6030_I2C_ADDR = 0x48  # ADDR pin pulled high on this breakout\n"
                "VL53L0X_I2C_ADDR  = 0x29\n"
                "AT42QT1070_I2C_ADDR = 0x1B\n"
                "\n"
                "# Calibration offsets — adjust after burn-in if needed\n"
                "TEMPERATURE_OFFSET = 0.0  # degrees C\n"
                "HUMIDITY_OFFSET    = 0.0  # percent RH\n"
                "\n"
                f'BACKLIGHT_PATH = "{backlight_path}"\n'
            )
            SENSOR_CONFIG_CANON.write_text(py_config)
            os.chmod(SENSOR_CONFIG_CANON, 0o600)

            # ── 3. Symlink into repo (protected from git reset --hard) ───────
            if SENSOR_CONFIG_LINK.exists() or SENSOR_CONFIG_LINK.is_symlink():
                SENSOR_CONFIG_LINK.unlink()
            if SENSOR_CONFIG_LINK.parent.exists():
                SENSOR_CONFIG_LINK.symlink_to(SENSOR_CONFIG_CANON)
                log.info(f"Symlinked {SENSOR_CONFIG_LINK} → {SENSOR_CONFIG_CANON}")

            # ── 4. Respond success, then reboot ──────────────────────────────
            self.send_json({"success": True})

            # Reboot after a short delay so the HTTP response reaches the client
            subprocess.Popen(["sh", "-c", "sleep 4 && reboot"])
            log.info("Reboot scheduled in 4 seconds")

        except Exception as e:
            log.error(f"handle_configure error: {e}")
            self.send_json({"success": False, "error": "Internal server error"}, 500)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Bind only to localhost — provisioning UI must not be exposed on the network
    server = HTTPServer(("127.0.0.1", PORT), ProvisioningHandler)
    log.info(f"Provisioning server listening on 127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Stopped")

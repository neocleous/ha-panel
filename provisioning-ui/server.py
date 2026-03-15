import http.server
import socketserver
import subprocess
import json
import os
import sys

PORT = 8080
UI_DIR = os.path.dirname(os.path.abspath(__file__))

class ProvisioningHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/networks':
            self.get_networks()
        elif self.path == '/status':
            self.get_status()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/connect':
            self.connect_network()
        else:
            self.send_error(404)

    def get_networks(self):
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'device', 'wifi', 'list'],
                capture_output=True, text=True, timeout=15
            )
            networks = []
            seen = set()
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 3 and parts[0] and parts[0] not in seen:
                    seen.add(parts[0])
                    networks.append({
                        'ssid': parts[0],
                        'signal': int(parts[1]) if parts[1].isdigit() else 0,
                        'secured': parts[2] != '--'
                    })
            networks.sort(key=lambda x: x['signal'], reverse=True)
            self.send_json(networks)
        except Exception as e:
            self.send_json([])

    def get_status(self):
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'STATE', 'general'],
                capture_output=True, text=True, timeout=5
            )
            state = result.stdout.strip()
            self.send_json({'state': state})
        except Exception as e:
            self.send_json({'state': 'unknown'})

    def connect_network(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            ssid = data.get('ssid', '').strip()
            password = data.get('password', '').strip()
            if not ssid:
                self.send_json({'success': False, 'error': 'No SSID provided'})
                return
            cmd = ['nmcli', 'device', 'wifi', 'connect', ssid]
            if password:
                cmd += ['password', password]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.send_json({'success': True})
            else:
                error = result.stderr.strip() or result.stdout.strip()
                if 'Secrets were required' in error or 'password' in error.lower():
                    self.send_json({'success': False, 'error': 'incorrect_password'})
                elif 'No network' in error or 'not found' in error.lower():
                    self.send_json({'success': False, 'error': 'network_not_found'})
                else:
                    self.send_json({'success': False, 'error': 'connection_failed'})
        except json.JSONDecodeError:
            self.send_json({'success': False, 'error': 'Invalid request'})
        except subprocess.TimeoutExpired:
            self.send_json({'success': False, 'error': 'timeout'})

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

def main():
    with socketserver.TCPServer(('', PORT), ProvisioningHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    main()

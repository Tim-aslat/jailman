#!/usr/bin/env python3.11

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

debug = config.getboolean('jailman', 'debug', fallback=False)
port = config.getint('jailman', 'port', fallback=8080)
secret_key = config.get('jailman', 'secret_key', fallback='defaultsecret')


hosts_str = config.get('jailman', 'host_allow', fallback='127.0.0.1')
host_allow = set(h.strip() for h in hosts_str.split(',') if h.strip())

print(f"Allowed hosts: {host_allow}")

bind_address = config.get('jailman', 'bind_address', fallback='127.0.0.1')

ALLOWED_JAILS = {"shell", "utils"}  # whitelist for safety

class JailControl(BaseHTTPRequestHandler):

    def get_validated_jail(self, parsed):
        query = urllib.parse.parse_qs(parsed.query)
        jail = query.get("jail", [None])[0]

        if not jail:
            self.send_error_response(400, "Missing jail name in query string")
            return None

#        if jail not in ALLOWED_JAILS:
#            msg = f"Jail '{jail}' is not whitelisted"
#            if debug:
#                msg += f" (Allowed: {', '.join(ALLOWED_JAILS)})"
#            self.send_error_response(403, msg)
#            return None

        return jail

    def log(self, message):
        print(f"[{self.client_address[0]}] {message}")


    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        client_ip = self.client_address[0]

        # Block early if host/IP not allowed
#        if client_ip not in host_allow:
#            self.send_error_response(403, "Forbidden: Access denied")
#            return

        # Handle API routes
        if parsed.path.startswith("/api/"):
#            api_key = self.headers.get("X-API-Key")
#            if api_key != secret_key:
#                self.send_error_response(403, "Forbidden: Invalid API key")
#                return

            if parsed.path == "/api/list_jails":
                self.handle_list_jails()
                return
            elif parsed.path == "/api/restart":
                self.handle_restart(parsed)
                return
            elif parsed.path == "/api/start":
                self.handle_start(parsed)
                return
            elif parsed.path == "/api/stop":
                self.handle_stop(parsed)
                return
            else:
                self.send_error_response(404, "API endpoint not found")
                return

        # Serve frontend static files
        path = parsed.path.lstrip("/")
        if not path:
            path = "index.html"

        try:
            with open(f"frontend/{path}", "rb") as f:
                self.send_response(200)
                if path.endswith(".html"):
                    self.send_header("Content-Type", "text/html")
                elif path.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript")
                elif path.endswith(".css"):
                    self.send_header("Content-Type", "text/css")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            # Only serve index.html for non-file routes (like /dashboard or /status)
            if "." not in path:
                try:
                    with open("frontend/index.html", "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        self.wfile.write(f.read())
                except FileNotFoundError:
                    self.send_error_response(404, "Frontend not found")
            else:
                self.send_error_response(404, "File not found")


    def handle_list_jails(self):
        try:
            result = subprocess.run(
                ["/usr/local/bin/bastille", "list", "-j"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
            self.send_json_response(result.stdout)
        except subprocess.CalledProcessError as e:
            self.send_text_response(500, e.output)

    def handle_restart(self, parsed):
        jail = self.get_validated_jail(parsed)
        if not jail:
            return

        try:
            result = subprocess.run(
                ["/usr/local/bin/bastille", "restart", jail],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
            self.send_text_response(200, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")
            self.send_text_response(500, e.output)

    def handle_start(self, parsed):
        jail = self.get_validated_jail(parsed)
        if not jail:
            return

        try:
            result = subprocess.run(
                ["/usr/local/bin/bastille", "start", jail],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
            self.send_text_response(200, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")
            self.send_text_response(500, e.output)

    def handle_stop(self, parsed):
        jail = self.get_validated_jail(parsed)
        if not jail:
            return

        try:
            result = subprocess.run(
                ["/usr/local/bin/bastille", "stop", jail],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
            self.send_text_response(200, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")
            self.send_text_response(500, e.output)

    # Helper to send JSON response
    def send_json_response(self, json_data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json_data.encode())

    # Helper to send plain text response
    def send_text_response(self, status, text):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    # Helper to send error responses (with text)
    def send_error_response(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode())


def run():
    server_address = (bind_address, port)
    httpd = HTTPServer(server_address, JailControl)
    print(f"Serving jail control API on http://{bind_address}:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

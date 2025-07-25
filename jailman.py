#!/usr/bin/env python3.11

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import json
import configparser
import sys
import base64
import signal
import os
import daemon
import atexit


config = configparser.ConfigParser()
config.read('config.ini')

debug = config.getboolean('jailman', 'debug', fallback=False)
port = config.getint('jailman', 'port', fallback=8080)
secret_key = config.get('jailman', 'secret_key', fallback='defaultsecret')

auth_user = config.get('jailman', 'auth_user', fallback=None)
auth_pass = config.get('jailman', 'auth_pass', fallback=None)

print(f"Username: {auth_user}\nPassword: {auth_pass}")


hosts_str = config.get('jailman', 'host_allow', fallback='127.0.0.1')
host_allow = set(h.strip() for h in hosts_str.split(',') if h.strip())

print(f"Allowed hosts: {host_allow}")

bind_address = config.get('jailman', 'bind_address', fallback='127.0.0.1')

ALLOWED_JAILS = {"shell", "utils"}  # whitelist for safety

class JailControl(BaseHTTPRequestHandler):

    def get_validated_jail(self, params):
        jail = params.get("jail")
        if not jail:
            self.send_error_response(400, "Missing jail name in query string")
            return None
        return jail

    def log(self, message):
        print(f"[{self.client_address[0]}] {message}")
        sys.stdout.flush()


    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        client_ip = self.client_address[0]

        # Parse query params
        query = urllib.parse.parse_qs(parsed.query)
        parsed_params = {k: v[0] for k, v in query.items()}

        # Handle API routes
        if parsed.path.startswith("/api/"):
            if parsed.path == "/api/list_jails":
                self.handle_list_jails()
                return
            elif parsed.path == "/api/restart":
                self.handle_restart(parsed_params)
                return
            elif parsed.path == "/api/start":
                self.handle_start(parsed_params)
                return
            elif parsed.path == "/api/stop":
                self.handle_stop(parsed_params)
                return
            elif parsed.path == "/api/snapshot":
                self.handle_snapshot(parsed_params)
                return
            elif parsed.path == "/api/set_boot":
                self.handle_boot_toggle(parsed_params)
                return
            elif parsed.path == "/api/set_priority":
                self.handle_priority_set(parsed_params)
                return
            else:
                self.send_error_response(404, "API endpoint not found")
                return

        # Serve frontend static files
        # Frontend basic auth check
        if auth_user and auth_pass:
            header = self.headers.get('Authorization')
            if not header or not header.startswith('Basic '):
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm="Jailman UI"')
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                if debug:
                    self.log("No Authorization header or incorrect format")
                return

            try:
                encoded = header.split(' ', 1)[1]
                decoded = base64.b64decode(encoded).decode('utf-8')
                username, _, password = decoded.partition(':')

                if debug:
                    self.log(f"Decoded Auth -> Username: {username}, Password: {password}")

                if username != auth_user or password != auth_pass:
                    if debug:
                        self.log("Auth failed: credentials don't match")
                    raise ValueError("Invalid credentials")

            except Exception as e:
                if debug:
                    self.log(f"Auth exception: {e}")
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm="Jailman UI"')
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid username or password.')
                return

        # Static file serving
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

    def handle_snapshot(self, parsed):
        jail = self.get_validated_jail(parsed)
        snapshot = parsed.get("snapshot")
        if not jail or not snapshot:
            self.send_text_response(400, "Missing jail or snapshot name")
            return

        try:
            result = subprocess.run(
                ["/usr/local/bin/bastille", "zfs", jail, "snapshot", snapshot],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
            self.send_text_response(200, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Snapshot command failed: {e.cmd}")
            self.send_text_response(500, e.output)

    def handle_boot_toggle(self, parsed):
        jail = self.get_validated_jail(parsed)
        state = parsed.get("boot")
        if not jail or state not in ("on", "off"):
            self.send_text_response(400, "Missing jail or invalid boot state (must be 'on' or 'off')")
            return

        try:
            result = subprocess.run(
                ["/usr/local/bin/bastille", "config", jail, "set", "boot", state],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
            self.send_text_response(200, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Boot toggle failed: {e.cmd}")
            self.send_text_response(500, e.output)

    def handle_priority_set(self, parsed):
        jail = self.get_validated_jail(parsed)
        priority = parsed.get("priority")
        if not jail or not priority or not priority.isdigit() or not 0 <= int(priority) <= 99:
            self.send_text_response(400, "Missing jail or invalid priority (0-99)")
            return

        try:
            result = subprocess.run(
                ["/usr/local/bin/bastille", "config", jail, "set", "priority", str(priority)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                text=True,
            )
            self.send_text_response(200, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Priority set failed: {e.cmd}")
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
    if debug == False:
        from daemon import DaemonContext
        import atexit
        import os
        import signal

        # Logging, PID file, and signal handling should already be set up earlier in the file

        def reload_config(signum, frame):
            logger.info("Received USR1 — reloading config...")
            config.read('config.ini')

        signal.signal(signal.SIGUSR1, reload_config)

        def cleanup():
            try:
                os.remove('/var/run/jailman.pid')
            except FileNotFoundError:
                pass

        atexit.register(cleanup)

        with DaemonContext():
            with open('/var/run/jailman.pid', 'w') as f:
                f.write(str(os.getpid()))
            run()
    else:
        run()

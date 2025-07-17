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

        if jail not in ALLOWED_JAILS:
            msg = f"Jail '{jail}' is not whitelisted"
            if debug:
                msg += f" (Allowed: {', '.join(ALLOWED_JAILS)})"
            self.send_error_response(403, msg)
            return None

        return jail


    def do_GET(self):
        print("do_GET triggered")
        client_ip = self.client_address[0]
        print(f"Client IP: {client_ip}")
        print(f"Allowed hosts: {host_allow}")
        if client_ip not in host_allow:
            print("Client not allowed, sending 403")
            self.send_error_response(403, "Forbidden: Access denied")
            return

        print("Client allowed, continuing...")

        api_key = self.headers.get("X-API-Key")
        if api_key != secret_key:
            print("Invalid or missing API key")
            self.send_error_response(403, "Forbidden: Invalid API key")
            return

        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/list_jails":
            self.handle_list_jails()
            return

        if parsed.path == "/restart":
            self.handle_restart(parsed)
            return

        if parsed.path == "/start":
            self.handle_start(parsed)
            return

        if parsed.path == "/stop":
            self.handle_stop(parsed)
            return

        self.send_error_response(404, "Not Found")

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

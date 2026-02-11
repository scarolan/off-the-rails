#!/usr/bin/env python3
"""Tiny HTTP server that serves tile-tools/ and handles POST /save to write catalog.json."""

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(TOOL_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                out = TOOL_DIR / "catalog.json"
                out.write_text(json.dumps(data, indent=2) + "\n")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "tiles": len(data.get("tiles", {}))}).encode())
                print(f"Saved catalog.json ({len(data.get('tiles', {}))} tiles)")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9005), Handler)
    print("Serving tile-tools on http://0.0.0.0:9005/")
    server.serve_forever()

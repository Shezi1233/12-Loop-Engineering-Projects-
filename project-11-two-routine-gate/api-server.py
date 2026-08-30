#!/usr/bin/env python3
"""Tiny API trigger for Routine B.

A bare-bones HTTP server that accepts POST /publish and runs Routine B.
In a real deployment this would be GitHub Actions `workflow_dispatch` or
a webhook; here it's a localhost-only server so you can curl it.

Usage:
    python api-server.py            # starts on localhost:8765

Then in another terminal:
    curl -X POST http://localhost:8765/publish
"""

import http.server
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent


class PublishHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/publish":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}')
            return

        # Run Routine B
        result = subprocess.run(
            [sys.executable, "routine-b.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
        )

        response = {
            "status": "PUBLISHED" if result.returncode == 0 else "FAILED",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        body = json.dumps(response, indent=2).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        sys.stderr.write(f"[api-server] {args[0]}\n")


def main():
    port = 8765
    server = http.server.HTTPServer(("127.0.0.1", port), PublishHandler)
    print(f"[api-server] listening on http://127.0.0.1:{port}")
    print(f"[api-server] POST /publish to fire Routine B")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[api-server] shutting down")
        server.server_close()


if __name__ == "__main__":
    main()
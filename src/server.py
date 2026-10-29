"""Stdlib-only HTTP server for TasteBridge. Run: python3 src/server.py
Routes: GET / (UI), GET /api/health, GET /api/demo, POST /api/plan {"prompt": ...}
No secrets: the mock client needs no key. The real client is NOT wired in
until the starter-kit Qloo key check passes (see docs/QLOO-API-KEY.md).
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(__file__))
from agent import build_plan  # noqa: E402

# Mode switch for deployment: QLOO_MODE=mock (default, safe) or live.
# Live mode fails fast at startup if QLOO_API_KEY is missing, so a
# deployed demo can never silently present mock results as live Qloo data.
MODE = os.environ.get("QLOO_MODE", "mock").lower()
if MODE == "live":
    from real_qloo import RealQlooClient  # noqa: E402
    try:
        CLIENT = RealQlooClient()
    except Exception as exc:  # noqa: BLE001 - startup must fail loudly
        raise SystemExit(f"QLOO_MODE=live but real client failed: {exc}")
else:
    from mock_qloo import MockQlooClient  # noqa: E402
    CLIENT = MockQlooClient()
PUBLIC = os.path.join(os.path.dirname(__file__), "..", "public")
PRESETS = [
    "Plan a romantic Bollywood evening in Los Angeles for 2, moderate budget",
    "Jazz evening in Los Angeles, moderate budget, for 4 friends",
    "Dreamy indie night in Los Angeles",
]


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send(200, json.dumps({"status": "ok", "mode": MODE}))
        elif path == "/api/demo":
            self._send(200, json.dumps({"presets": PRESETS}))
        elif path in ("/", "/index.html"):
            with open(os.path.join(PUBLIC, "index.html"), "rb") as fh:
                self._send(200, fh.read(), "text/html; charset=utf-8")
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if urlparse(self.path).path != "/api/plan":
            self._send(404, json.dumps({"error": "not found"}))
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        plan, trace = build_plan(CLIENT, payload.get("prompt", ""))
        self._send(200, json.dumps({"plan": plan, "trace": trace}))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    print(f"TasteBridge running on http://0.0.0.0:{port} ({MODE} mode)")
    # 0.0.0.0 (not 127.0.0.1) so a public host container can reach it.
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()

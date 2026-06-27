"""Zero-dependency HTTP server for the IELTS Speaking demo.

Run:  python3 server.py           # serves http://localhost:8000
Env:  TAVUS_API_KEY   (required for a REAL call; without it, runs in demo mode)
      TAVUS_PAL_ID    (default pea55f8508c2)
      TAVUS_FACE_ID   (default r68fe8906e53)
      PORT            (default 8000)
      DEMO_MODE=1     force a fake conversation_url (no Tavus call / no credits)

Endpoints:
  POST /api/start-test   {parts:[1,2,3], candidate_name?}  -> {conversation_url, conversation_id}
  POST /api/score        <flat band report>                -> stores it (Tavus post-call receiver)
  GET  /api/report/<id>                                    -> {status, report?}
  GET  /                                                   -> static UI
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from app_core import App, SAMPLE_REPORT

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
DEMO_MODE = os.environ.get("DEMO_MODE") == "1" or not os.environ.get("TAVUS_API_KEY")

STATIC_TYPES = {".html": "text/html; charset=utf-8",
                ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".ico": "image/x-icon"}


def demo_creator(payload):
    """Fake conversation for offline demos / no credits."""
    return {
        "conversation_id": "demo-conversation",
        "conversation_url": "https://tavus.daily.co/demo-conversation",
        "status": "demo",
    }


def make_app():
    if DEMO_MODE:
        # no real Tavus calls; the "Load sample report" button drives the report path
        return App(conversation_creator=demo_creator, api_key="",
                   report_fetcher=lambda cid: None,
                   conversation_ender=lambda cid: None)
    return App()  # real Tavus creator/fetcher/ender


APP = make_app()


class Handler(BaseHTTPRequestHandler):
    server_version = "ielts-demo/1.0"

    def _send_json(self, status, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    # ---- routes ----------------------------------------------------------

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        if body is None:
            return self._send_json(400, {"error": "invalid JSON body"})

        if path == "/api/start-test":
            status, out = APP.handle_start_test(body)
            if status == 200:
                out["demo_mode"] = DEMO_MODE
            return self._send_json(status, out)
        if path == "/api/score":
            status, out = APP.handle_score(body)
            return self._send_json(status, out)
        if path == "/api/end-test":
            status, out = APP.handle_end_test(body.get("conversation_id"))
            return self._send_json(status, out)
        return self._send_json(404, {"error": "not found"})

    def do_GET(self):
        path = urlparse(self.path).path

        if path.startswith("/api/report/"):
            conversation_id = path[len("/api/report/"):]
            status, out = APP.handle_report(conversation_id)
            return self._send_json(status, out)
        if path == "/api/config":
            return self._send_json(200, {"demo_mode": DEMO_MODE,
                                         "sample_report": SAMPLE_REPORT})
        return self._serve_static(path)

    def _serve_static(self, path):
        if path in ("/", ""):
            path = "/index.html"
        # prevent path traversal
        safe = os.path.normpath(path).lstrip("/")
        full = os.path.join(PUBLIC_DIR, safe)
        if not full.startswith(PUBLIC_DIR) or not os.path.isfile(full):
            return self._send_json(404, {"error": "not found"})
        ext = os.path.splitext(full)[1]
        ctype = STATIC_TYPES.get(ext, "application/octet-stream")
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass  # quiet


def main():
    port = int(os.environ.get("PORT", "8000"))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    mode = "DEMO (no Tavus call)" if DEMO_MODE else "LIVE (real Tavus calls)"
    print(f"IELTS demo server on http://localhost:{port}  [{mode}]")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


VERSION = os.environ.get("APP_VERSION", "1.0.0")


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/livez", "/readyz"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        if self.path == "/":
            body = json.dumps({"service": "release-lab", "version": VERSION, "status": "ok"})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return

        self.send_error(404)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), RequestHandler).serve_forever()
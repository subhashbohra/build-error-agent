import http.server
import socketserver
import json
import os
import uuid
from urllib.parse import urlparse
from .worker import enqueue_job

PORT = int(os.environ.get("PORT", "8080"))
AGENT_SECRET = os.environ.get("AGENT_SECRET")


class Handler(http.server.BaseHTTPRequestHandler):
    def _set_json(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == '/health':
            self._set_json(200)
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        p = urlparse(self.path)
        if p.path != '/webhook':
            self.send_response(404)
            self.end_headers()
            return

        # auth
        agent_secret = self.headers.get('X-Agent-Secret')
        if AGENT_SECRET and agent_secret != AGENT_SECRET:
            self._set_json(401)
            self.wfile.write(json.dumps({'error': 'invalid agent secret'}).encode())
            return

        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length) if length > 0 else b'{}'
        try:
            payload = json.loads(body.decode())
        except Exception:
            payload = {}

        job_id = str(uuid.uuid4())
        enqueue_job({'id': job_id, 'payload': payload})

        self._set_json(202)
        self.wfile.write(json.dumps({'status': 'accepted', 'job_id': job_id}).encode())


def run():
    with socketserver.ThreadingTCPServer(('0.0.0.0', PORT), Handler) as httpd:
        print(f"Agent listening on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()


if __name__ == '__main__':
    run()

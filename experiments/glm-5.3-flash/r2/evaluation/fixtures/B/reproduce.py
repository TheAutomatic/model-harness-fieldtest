"""Reproduce the redirect bug using a local HTTP server, without internet."""
import sys
from pathlib import Path
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests

seen = []


class Handler(BaseHTTPRequestHandler):
    def handle_request(self):
        self.rfile.read(int(self.headers.get('Content-Length', 0)))
        seen.append(self.command)
        status = (303, 307, 200)[len(seen) - 1]
        self.send_response(status)
        if status != 200:
            self.send_header('Location', '/second' if len(seen) == 1 else '/done')
        self.send_header('Content-Length', '0')
        self.end_headers()

    do_POST = do_GET = handle_request

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with requests.Session() as session:
            session.trust_env = False
            session.post('http://127.0.0.1:%s/start' % server.server_port,
                         data='hello', timeout=3)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    print('Expected: POST -> GET -> GET')
    print('Actual:   ' + ' -> '.join(seen))
    sys.exit(0 if seen == ['POST', 'GET', 'GET'] else 1)

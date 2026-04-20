from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'frontend'
PORT = 5173


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = self.translate_path(self.path)
        requested = Path(path)
        if requested.exists() and requested.is_file():
            return super().do_GET()
        self.path = '/index.html'
        return super().do_GET()


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), FrontendHandler)
    print(f'Frontend server listening on http://127.0.0.1:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

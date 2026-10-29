"""Preview a generated page beneath its GitHub Pages repository subpath.

Unlike `python -m http.server`, this answers HTTP range requests, which browsers need
before they allow seeking in <video> (GitHub Pages supports them too).

    python preview_server.py --root docs --base my-repo --port 8000
    # then open http://127.0.0.1:8000/my-repo/
"""
import argparse
import os
import re
import socket
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, base, **kwargs):
        self.base = base
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.base != '/' and self.path in ('/', self.base.rstrip('/')):
            self.send_response(302)
            self.send_header('Location', self.base)
            self.end_headers()
            return
        if not self.path.startswith(self.base):
            self.send_error(404, f'Pages are served under {self.base}')
            return
        self.path = '/' + self.path[len(self.base):]
        if not self.send_range():
            super().do_GET()

    def send_range(self):
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', self.headers.get('Range', '').strip())
        path = self.translate_path(self.path)
        if not match or not os.path.isfile(path):
            return False
        size = os.path.getsize(path)
        start, end = match.groups()
        if start:
            start, end = int(start), min(int(end) if end else size - 1, size - 1)
        else:
            start, end = max(0, size - int(end or 0)), size - 1
        if start > end or start >= size:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers()
            return True
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        with open(path, 'rb') as file:
            file.seek(start)
            remaining = end - start + 1
            try:
                while remaining:
                    chunk = file.read(min(64 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass  # Browsers cancel range requests freely while seeking.
        return True


class Server(ThreadingHTTPServer):
    # On Windows, SO_REUSEADDR lets a second server bind a port that another server is still
    # listening on, and requests keep reaching the old one. Claim the port exclusively there.
    allow_reuse_address = os.name != 'nt'

    def server_bind(self):
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', default='.', help='directory containing index.html')
    parser.add_argument('--base', default='', help='repository name served as the subpath, e.g. my-repo for /my-repo/')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    base = '/' + args.base.strip('/') + '/' if args.base.strip('/') else '/'
    handler = partial(Handler, base=base, directory=os.path.abspath(args.root))
    try:
        server = Server(('127.0.0.1', args.port), handler)
    except OSError:
        sys.exit(f'Port {args.port} is not available. '
                 'Another server may still be running; stop it or choose another --port.')
    print(f'Serving {os.path.abspath(args.root)} at http://127.0.0.1:{args.port}{base}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()

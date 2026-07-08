#!/usr/bin/env python3
"""Photo viewer — serves a browser-based gallery from a local HTTP server."""

import http.server
import json
import os
import shutil
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import unquote


SUPPORTED = {'.jpg', '.jpeg', '.png', '.gif', '.tiff', '.tif', '.bmp'}

MIME_TYPES = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff',
    '.bmp': 'image/bmp',
}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Photo Viewer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #111; color: #ddd; font-family: -apple-system, sans-serif;
         display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
  #viewer { flex: 1; display: flex; align-items: center; justify-content: center;
            overflow: hidden; position: relative; }
  #photo { max-width: 100%; max-height: 100%; object-fit: contain;
           display: block; user-select: none; }
  #bar { display: flex; align-items: center; justify-content: space-between;
         padding: 10px 20px; background: #1a1a1a; flex-shrink: 0; }
  #info { font-size: 14px; color: #aaa; text-align: center; flex: 1; }
  button { background: #333; color: #eee; border: none; padding: 8px 20px;
           font-size: 15px; border-radius: 4px; cursor: pointer; }
  button:hover { background: #555; }
</style>
</head>
<body>
<div id="viewer">
  <img id="photo" src="" alt="">
</div>
<div id="bar">
  <button onclick="go(-1)">&#9664; Prev</button>
  <div id="info"></div>
  <button onclick="go(1)">Next &#9654;</button>
</div>
<script>
const photos = PHOTOS_JSON;
let idx = 0;

function show() {
  const p = photos[idx];
  document.getElementById('photo').src = '/img?path=' + encodeURIComponent(p.path);
  document.getElementById('info').textContent =
    p.name + '   |   ' + p.date + '   |   ' + (idx+1) + ' of ' + photos.length;
  document.title = p.name;
}

function go(delta) {
  idx = (idx + delta + photos.length) % photos.length;
  show();
}

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ') go(1);
  else if (e.key === 'ArrowLeft') go(-1);
});

show();
</script>
</body>
</html>
"""


def load_photos(folder):
    from datetime import datetime
    photos = []
    for p in sorted(Path(folder).iterdir()):
        if p.is_file() and p.suffix.lower() in SUPPORTED:
            mtime = os.path.getmtime(p)
            date_str = datetime.fromtimestamp(mtime).strftime('%B %d, %Y')
            photos.append({'name': p.name, 'path': str(p), 'date': date_str})
    return photos


class Handler(http.server.BaseHTTPRequestHandler):
    photos = []
    allowed_paths = set()

    def log_message(self, *_):
        pass  # silence request logs

    def do_GET(self):
        if self.path == '/':
            page = HTML.replace('PHOTOS_JSON', json.dumps(self.photos))
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(page.encode())

        elif self.path.startswith('/img?path='):
            raw = self.path[len('/img?path='):]
            path = unquote(raw)
            if path not in self.allowed_paths:
                self.send_error(403, "Forbidden")
                return
            try:
                ext = Path(path).suffix.lower()
                mime = MIME_TYPES.get(ext, 'application/octet-stream')
                with open(path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-Type', mime)
                    self.send_header('Content-Length', str(os.path.getsize(path)))
                    self.end_headers()
                    shutil.copyfileobj(f, self.wfile)
            except OSError as e:
                self.send_error(404, str(e))
        else:
            self.send_error(404)


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    photos = load_photos(folder)
    if not photos:
        print(f"No supported images found in: {folder}")
        sys.exit(1)

    print(f"Found {len(photos)} photos in {folder}")

    Handler.photos = photos
    Handler.allowed_paths = {p['path'] for p in photos}

    server = http.server.HTTPServer(('127.0.0.1', 0), Handler)
    port = server.server_address[1]
    url = f'http://127.0.0.1:{port}'
    print(f"Serving at {url}  (Ctrl+C to quit)")

    threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDone.")


if __name__ == '__main__':
    main()

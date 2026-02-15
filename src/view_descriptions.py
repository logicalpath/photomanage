"""Simple HTTP server to view images alongside their SmolVLM2 descriptions."""

import argparse
import html
import json
import mimetypes
import sqlite3
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = PROJECT_ROOT / "outputs" / "image_analysis.json"
IMAGE_ROOT = PROJECT_ROOT / "database" / "512x512"
MEDIAMETA_DB = PROJECT_ROOT / "database" / "mediameta.db"


def load_photo_dates() -> dict[str, str]:
    """Load DateTimeOriginal from the exif table, keyed by SourceFile path."""
    if not MEDIAMETA_DB.is_file():
        return {}
    conn = sqlite3.connect(str(MEDIAMETA_DB))
    rows = conn.execute("SELECT SourceFile, DateTimeOriginal FROM exif WHERE DateTimeOriginal != ''").fetchall()
    conn.close()
    return {path: date for path, date in rows}


def build_html(entries: list[dict], dates: dict[str, str]) -> str:
    cards = []
    for entry in entries:
        if entry.get("error"):
            continue
        file_path = entry["file"]  # e.g. "./0/0001b8b0-...JPG"
        desc = html.escape(entry.get("description", ""))
        gen_time = entry.get("generation_time_seconds", 0)
        raw_date = dates.get(file_path, "")
        photo_date = html.escape(raw_date.replace("T", " ")) if raw_date else "unknown date"
        img_src = f"/images/{file_path.removeprefix('./')}"
        cards.append(
            f"""<div class="card">
  <img src="{img_src}" alt="{desc}" loading="lazy">
  <div class="info">
    <p class="desc">{desc}</p>
    <p class="meta">{photo_date} &middot; {gen_time:.1f}s &middot; {html.escape(file_path)}</p>
  </div>
</div>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Image Descriptions</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: system-ui, sans-serif; background: #f5f5f5; padding: 1rem; }}
  h1 {{ text-align: center; margin-bottom: 1rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }}
  .card {{ background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.12); }}
  .card img {{ width: 100%; height: 300px; object-fit: cover; display: block; }}
  .info {{ padding: .75rem; }}
  .desc {{ margin-bottom: .25rem; }}
  .meta {{ font-size: .8rem; color: #888; }}
</style>
</head>
<body>
<h1>Image Descriptions ({len(cards)} images)</h1>
<div class="grid">
{"".join(cards)}
</div>
</body>
</html>"""


class Handler(SimpleHTTPRequestHandler):
    html_content: str = ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        if path == "/" or path == "/index.html":
            data = self.html_content.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path.startswith("/images/"):
            rel = path.removeprefix("/images/")
            file_path = IMAGE_ROOT / rel
            if file_path.is_file():
                ctype, _ = mimetypes.guess_type(str(file_path))
                data = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", ctype or "application/octet-stream")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        self.send_error(404)

    def log_message(self, format, *args):
        pass  # silence per-request logs


def main():
    parser = argparse.ArgumentParser(description="View image descriptions in a browser")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on (default: 8080)")
    args = parser.parse_args()

    entries = json.loads(JSON_PATH.read_text())
    dates = load_photo_dates()
    Handler.html_content = build_html(entries, dates)

    server = HTTPServer(("localhost", args.port), Handler)
    print(f"Serving {len(entries)} images at http://localhost:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

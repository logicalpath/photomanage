import asyncio
import io
import logging
import sqlite3
import os

from datasette import hookimpl
from datasette.utils.asgi import Response

logger = logging.getLogger(__name__)

_default_database_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "database")
)
MEDIAMETA_DB_PATH = os.getenv(
    "MEDIAMETA_DB_PATH",
    os.path.join(_default_database_dir, "mediameta.db"),
)

RAW_EXTENSIONS = {"nef", "cr2", "cr3", "arw", "dng", "raf", "orf", "rw2", "pef", "srw"}


def _convert_raw_to_jpeg(filepath: str) -> bytes:
    import rawpy
    from PIL import Image

    with rawpy.imread(filepath) as raw:
        rgb = raw.postprocess()
    img = Image.fromarray(rgb)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


async def raw_photo_handler(request, datasette):
    filename = request.url_vars.get("filename", "")
    if not filename:
        return Response("Missing filename", status=400, content_type="text/plain")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in RAW_EXTENSIONS:
        return Response("Not a RAW file", status=400, content_type="text/plain")

    try:
        with sqlite3.connect(MEDIAMETA_DB_PATH) as conn:
            row = conn.execute(
                "SELECT full_path FROM exif_with_fullpath WHERE FileName = ?",
                (filename,),
            ).fetchone()
    except sqlite3.Error as e:
        logger.error("Database error looking up %s: %s", filename, e)
        return Response("Internal server error", status=500, content_type="text/plain")

    if not row:
        return Response("Photo not found", status=404, content_type="text/plain")

    full_path = row[0]
    if not os.path.exists(full_path):
        return Response("File not on disk", status=404, content_type="text/plain")

    try:
        loop = asyncio.get_running_loop()
        jpeg_bytes = await loop.run_in_executor(None, _convert_raw_to_jpeg, full_path)
    except Exception as e:
        logger.error("RAW conversion failed for %s: %s", full_path, e)
        return Response("Conversion failed", status=500, content_type="text/plain")

    return Response(
        jpeg_bytes,
        status=200,
        headers={"Cache-Control": "max-age=3600"},
        content_type="image/jpeg",
    )


@hookimpl
def register_routes():
    return [
        (r"^/raw-photo/(?P<filename>.+)$", raw_photo_handler),
    ]

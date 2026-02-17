import struct
import sqlite3
import math
import os
import re
import threading

from datasette import hookimpl
from datasette.utils.asgi import Response

_model = None
_embeddings_cache = None
_lock = threading.Lock()

# Allow database paths to be configured via environment variables, with
# sensible defaults based on the current file location.
_default_database_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "database")
)
EMBEDDINGS_DB_PATH = os.getenv(
    "EMBEDDINGS_DB_PATH",
    os.path.join(_default_database_dir, "embeddings-vlm2.db"),
)
MEDIAMETA_DB_PATH = os.getenv(
    "MEDIAMETA_DB_PATH",
    os.path.join(_default_database_dir, "mediameta.db"),
)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MAX_QUERY_LENGTH = 500


def _get_model():
    global _model
    with _lock:
        if _model is None:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _load_embeddings():
    global _embeddings_cache
    with _lock:
        if _embeddings_cache is not None:
            return _embeddings_cache

        try:
            with sqlite3.connect(EMBEDDINGS_DB_PATH) as conn:
                rows = conn.execute(
                    "SELECT id, embedding, content FROM embeddings WHERE collection_id = 1"
                ).fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to load embeddings: {e}")

        embeddings_cache = []
        for row_id, embedding_blob, content in rows:
            num_floats = len(embedding_blob) // 4
            vector = struct.unpack(f"{num_floats}f", embedding_blob)
            norm = math.sqrt(sum(x * x for x in vector))
            embeddings_cache.append((row_id, vector, norm, content))

        _embeddings_cache = embeddings_cache
    return _embeddings_cache


def _cosine_similarity(vec_a, norm_a, vec_b, norm_b):
    if norm_a == 0 or norm_b == 0:
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return dot / (norm_a * norm_b)


async def search_handler(request, datasette):
    q = request.args.get("q", "").strip()
    if not q:
        return Response.json({"error": "Missing 'q' parameter"}, status=400)
    if len(q) > _MAX_QUERY_LENGTH:
        return Response.json(
            {"error": f"Query too long (max {_MAX_QUERY_LENGTH} characters)"},
            status=400,
        )

    try:
        n = int(request.args.get("n", "20"))
    except ValueError:
        n = 20
    n = max(1, min(n, 200))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    # Validate date format
    if start_date and not _DATE_RE.match(start_date):
        start_date = ""
    if end_date and not _DATE_RE.match(end_date):
        end_date = ""

    # If date filters are provided, build a map of SourceFile -> CreateDate
    # so we can restrict search results to the date range
    date_map = {}
    date_filter_ids = None
    if start_date or end_date:
        try:
            with sqlite3.connect(MEDIAMETA_DB_PATH) as conn:
                sql = "SELECT SourceFile, CreateDate FROM exif WHERE CreateDate IS NOT NULL"
                params = []
                if start_date:
                    sql += " AND CreateDate >= ?"
                    params.append(start_date)
                if end_date:
                    sql += " AND (CreateDate <= ? || ' 23:59:59' OR CreateDate LIKE ? || '%')"
                    params.extend([end_date, end_date])
                rows = conn.execute(sql, params).fetchall()
        except sqlite3.Error:
            return Response.json(
                {"error": "Unable to perform search. Please try again later."},
                status=500,
            )
        date_map = {row[0]: row[1] for row in rows}
        date_filter_ids = set(date_map.keys())

    try:
        model = _get_model()
        all_embeddings = _load_embeddings()
    except RuntimeError:
        return Response.json(
            {"error": "Unable to perform search. Please try again later."},
            status=500,
        )

    query_embedding = model.encode(q).tolist()
    query_norm = math.sqrt(sum(x * x for x in query_embedding))

    scores = []
    for row_id, vector, norm, content in all_embeddings:
        if date_filter_ids is not None and row_id not in date_filter_ids:
            continue
        score = _cosine_similarity(query_embedding, query_norm, vector, norm)
        scores.append((score, row_id, content))

    scores.sort(key=lambda x: x[0], reverse=True)

    top_scores = scores[:n]

    # If no date filter was applied, look up dates for the top results
    if date_filter_ids is None:
        source_files = [row_id for _, row_id, _ in top_scores]
        if source_files:
            try:
                with sqlite3.connect(MEDIAMETA_DB_PATH) as conn:
                    placeholders = ",".join("?" for _ in source_files)
                    rows = conn.execute(
                        f"SELECT SourceFile, CreateDate FROM exif WHERE SourceFile IN ({placeholders})",
                        source_files,
                    ).fetchall()
                date_map = {row[0]: row[1] for row in rows}
            except sqlite3.Error:
                pass

    results = []
    for score, row_id, content in top_scores:
        results.append(
            {
                "id": row_id,
                "score": round(score, 4),
                "content": content or "",
                "date": date_map.get(row_id) or "",
            }
        )

    return Response.json(results)


@hookimpl
def register_routes():
    return [
        (r"^/search$", search_handler),
    ]

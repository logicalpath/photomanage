import struct
import sqlite3
import math
import os

from datasette import hookimpl
from datasette.utils.asgi import Response

_model = None
_embeddings_cache = None

EMBEDDINGS_DB_PATH = os.path.join(os.path.dirname(__file__), "../../database/embeddings.db")
MEDIAMETA_DB_PATH = os.path.join(os.path.dirname(__file__), "../../database/mediameta.db")


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _load_embeddings():
    global _embeddings_cache
    if _embeddings_cache is not None:
        return _embeddings_cache

    db_path = os.path.normpath(EMBEDDINGS_DB_PATH)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT id, embedding, content FROM embeddings WHERE collection_id = 1"
    ).fetchall()
    conn.close()

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

    try:
        n = int(request.args.get("n", "20"))
    except ValueError:
        n = 20
    n = max(1, min(n, 200))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    # If date filters are provided, build a map of SourceFile -> CreateDate
    # so we can restrict search results to the date range
    date_map = {}
    date_filter_ids = None
    if start_date or end_date:
        meta_path = os.path.normpath(MEDIAMETA_DB_PATH)
        conn = sqlite3.connect(meta_path)
        sql = "SELECT SourceFile, CreateDate FROM exif WHERE CreateDate IS NOT NULL"
        params = []
        if start_date:
            sql += " AND CreateDate >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND (CreateDate <= ? || ' 23:59:59' OR CreateDate LIKE ? || '%')"
            params.extend([end_date, end_date])
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        date_map = {row[0]: row[1] for row in rows}
        date_filter_ids = set(date_map.keys())

    model = _get_model()
    query_embedding = model.encode(q).tolist()
    query_norm = math.sqrt(sum(x * x for x in query_embedding))

    all_embeddings = _load_embeddings()

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
            meta_path = os.path.normpath(MEDIAMETA_DB_PATH)
            conn = sqlite3.connect(meta_path)
            placeholders = ",".join("?" for _ in source_files)
            rows = conn.execute(
                f"SELECT SourceFile, CreateDate FROM exif WHERE SourceFile IN ({placeholders})",
                source_files,
            ).fetchall()
            conn.close()
            date_map = {row[0]: row[1] for row in rows}

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

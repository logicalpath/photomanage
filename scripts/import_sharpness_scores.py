#!/usr/bin/env python3
"""
Import Laplacian sharpness scores into the image_sharpness table in mediameta.db.

Reads outputs/v2/sharpness_scores.json (produced by scripts/laplacian_sharpness.py)
and upserts records keyed on SourceFile. Safe to run multiple times.

Usage:
    python scripts/import_sharpness_scores.py
    python scripts/import_sharpness_scores.py --json-file outputs/v2/sharpness_scores.json
    python scripts/import_sharpness_scores.py --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

import sqlite_utils


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_JSON = PROJECT_ROOT / "outputs" / "v2" / "sharpness_scores.json"
DEFAULT_DB = PROJECT_ROOT / "database" / "mediameta.db"


def main():
    parser = argparse.ArgumentParser(description="Import sharpness scores into mediameta.db")
    parser.add_argument("--json-file", type=Path, default=DEFAULT_JSON, help=f"Input JSON file (default: {DEFAULT_JSON})")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"SQLite database (default: {DEFAULT_DB})")
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing to database")
    args = parser.parse_args()

    if not args.json_file.exists():
        print(f"Error: JSON file not found: {args.json_file}")
        print("Run scripts/laplacian_sharpness.py first.")
        sys.exit(1)

    with open(args.json_file) as f:
        raw = json.load(f)

    records = [{"SourceFile": r["file"], "sharpness": r["sharpness"]} for r in raw if r.get("sharpness") is not None]
    missing = len(raw) - len(records)

    print(f"Records in JSON:  {len(raw):,}")
    print(f"With scores:      {len(records):,}")
    if missing:
        print(f"Missing/skipped:  {missing:,}")

    if args.dry_run:
        print("Dry run — sample records:")
        for r in records[:3]:
            print(" ", r)
        return

    db = sqlite_utils.Database(args.db)
    db["image_sharpness"].upsert_all(records, pk="SourceFile", alter=True)

    count = db["image_sharpness"].count
    print(f"image_sharpness table now has {count:,} rows")
    print("Done.")


if __name__ == "__main__":
    main()

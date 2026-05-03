#!/usr/bin/env python3
"""
Import camera/lens/exposure EXIF data into the exif_camera table in mediameta.db.

Reads the JSON output from get_camera_exif.sh and upserts records keyed on
SourceFile. Safe to run multiple times.

Usage:
    python scripts/import_camera_exif.py
    python scripts/import_camera_exif.py --json-file outputs/camera_exif.json
    python scripts/import_camera_exif.py --dry-run
"""

import argparse
import json
import os
import sys
from pathlib import Path

import sqlite_utils


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_JSON = PROJECT_ROOT / "outputs" / "camera_exif.json"
DEFAULT_DB = PROJECT_ROOT / "database" / "mediameta.db"

# Map exiftool output keys to table column names
FIELD_MAP = {
    "SourceFile": "SourceFile",
    "FileName": "FileName",
    "Make": "Make",
    "Model": "Model",
    "LensModel": "LensModel",
    "FocalLength": "FocalLength",
    "FocalLengthIn35mmFormat": "FocalLengthIn35mm",
    "MaxApertureValue": "MaxApertureValue",
    "ExposureTime": "ExposureTime",
    "FNumber": "FNumber",
    "ISO": "ISO",
    "ExposureMode": "ExposureMode",
    "ExposureProgram": "ExposureProgram",
    "MeteringMode": "MeteringMode",
    "FocusMode": "FocusMode",
    "FocusDistance": "FocusDistance",
    "SubjectDistance": "SubjectDistance",
    "Sharpness": "Sharpness",
    "BrightnessValue": "BrightnessValue",
    "Flash": "Flash",
    "WhiteBalance": "WhiteBalance",
}


def normalize_source_file(path: str, source_dir: str) -> str:
    """Convert absolute path to ./subdir/filename format used in other tables."""
    p = Path(path)
    src = Path(source_dir)
    try:
        rel = p.relative_to(src)
        return "./" + rel.as_posix()
    except ValueError:
        return path


def main():
    parser = argparse.ArgumentParser(description="Import camera EXIF data into mediameta.db")
    parser.add_argument("--json-file", type=Path, default=DEFAULT_JSON, help=f"Input JSON file (default: {DEFAULT_JSON})")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"SQLite database (default: {DEFAULT_DB})")
    parser.add_argument(
        "--source-dir",
        default=os.environ.get("MEDIA_SOURCE_DIR", "/Volumes/Eddie 4TB/MediaFiles/uuid"),
        help="Source media root for SourceFile normalization (default: $MEDIA_SOURCE_DIR or /Volumes/Eddie 4TB/MediaFiles/uuid)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing to database")
    args = parser.parse_args()

    if not args.json_file.exists():
        print(f"Error: JSON file not found: {args.json_file}")
        print("Run scripts/get_camera_exif.sh first.")
        sys.exit(1)

    print(f"Loading {args.json_file}...")
    with open(args.json_file, encoding="utf-8") as f:
        raw = json.load(f)

    print(f"Records in JSON: {len(raw):,}")

    records = []
    for item in raw:
        row = {}
        for src_key, col in FIELD_MAP.items():
            val = item.get(src_key)
            if val is not None:
                row[col] = val
        if "SourceFile" in row:
            row["SourceFile"] = normalize_source_file(row["SourceFile"], args.source_dir)
        if row:
            records.append(row)

    non_empty = sum(1 for r in records if len(r) > 2)  # more than just SourceFile + FileName
    print(f"Records with camera data: {non_empty:,}")

    if args.dry_run:
        print("Dry run — sample record:")
        for r in records[:3]:
            print(" ", r)
        return

    db = sqlite_utils.Database(args.db)
    db["exif_camera"].upsert_all(records, pk="SourceFile", alter=True)

    count = db["exif_camera"].count
    print(f"exif_camera table now has {count:,} rows")
    print("Done.")


if __name__ == "__main__":
    main()

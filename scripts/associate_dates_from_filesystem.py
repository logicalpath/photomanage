#!/usr/bin/env python3
"""
Populate date_associations for image files whose originals still exist on disk,
using the filesystem mtime as the date source.

Usage:
    python3 scripts/associate_dates_from_filesystem.py <folder> [--dry-run] [--force]

The script:
  1. Lists image files in <folder>
  2. Looks up each filename in the mappings table to find its UUID
  3. Checks that the UUID exists in exif with no CreateDate
  4. Skips files that already have a date_associations row, unless --force is given
  5. Inserts a date_associations row using the original file's mtime
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "mediameta.db"
SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".tiff", ".tif", ".bmp", ".heic"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", help="Folder containing original image files")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be inserted without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing date_associations rows (including manual entries)")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Error: not a directory: {folder}", file=sys.stderr)
        sys.exit(1)

    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not files:
        print(f"No supported image files found in {folder}")
        sys.exit(0)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = skipped_no_mapping = skipped_has_date = skipped_not_in_exif = skipped_already_associated = 0

    for p in files:
        cur.execute('SELECT "New Name" FROM mappings WHERE "Old Name" = ?', (p.name,))
        row = cur.fetchone()
        if not row:
            print(f"  no mapping: {p.name}")
            skipped_no_mapping += 1
            continue

        uuid = row[0]

        cur.execute("SELECT SourceFile, CreateDate FROM exif WHERE FileName = ?", (uuid,))
        exif_row = cur.fetchone()
        if not exif_row:
            print(f"  not in exif: {p.name} -> {uuid}")
            skipped_not_in_exif += 1
            continue

        source_file, create_date = exif_row
        if create_date:
            print(f"  has date ({create_date[:10]}): {p.name} -> {uuid}")
            skipped_has_date += 1
            continue

        cur.execute("SELECT date FROM date_associations WHERE SourceFile = ?", (source_file,))
        existing = cur.fetchone()
        if existing and not args.force:
            print(f"  already associated ({existing[0]}): {p.name} -> {uuid}")
            skipped_already_associated += 1
            continue

        mtime = os.path.getmtime(p)
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        if args.dry_run:
            print(f"  would insert: {p.name} -> {uuid}  date={date_str}  source=filesystem")
        else:
            cur.execute(
                "INSERT OR REPLACE INTO date_associations (SourceFile, date, source, note) VALUES (?, ?, ?, ?)",
                (source_file, date_str, "filesystem", f"mtime of original: {p}"),
            )
            print(f"  inserted: {p.name} -> {uuid}  date={date_str}")
        inserted += 1

    if not args.dry_run:
        conn.commit()

    print(f"\n{'Would insert' if args.dry_run else 'Inserted'}: {inserted}  |  "
          f"no mapping: {skipped_no_mapping}  |  "
          f"already has date: {skipped_has_date}  |  "
          f"not in exif: {skipped_not_in_exif}  |  "
          f"already associated: {skipped_already_associated}")


if __name__ == "__main__":
    main()

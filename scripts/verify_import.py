#!/usr/bin/env python3
"""
Verify image descriptions were imported correctly to the database.

Compares record counts by file extension between JSON and database,
excluding "Skipped for now" placeholder records.

Usage:
    python scripts/verify_import.py
    python scripts/verify_import.py --json-file outputs/image_analysis.json
    python scripts/verify_import.py --database database/mediameta.db
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


SKIP_DESCRIPTION = "Skipped for now"
SKIP_MODEL = "skipped"


def get_extension(file_path: str) -> str:
    """Extract and normalize file extension."""
    ext = Path(file_path).suffix.upper().lstrip('.')
    return ext if ext else "(none)"


def count_json_by_extension(json_path: Path) -> tuple[Counter, int]:
    """
    Count records by extension in JSON file.
    Excludes skipped records.
    Returns (counter, skipped_count)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    counter = Counter()
    skipped = 0

    for record in data:
        # Skip placeholder records
        if (record.get('description') == SKIP_DESCRIPTION and
                record.get('model') == SKIP_MODEL):
            skipped += 1
            continue

        ext = get_extension(record.get('file', ''))
        counter[ext] += 1

    return counter, skipped


def count_database_by_extension(db_path: Path, table: str) -> Counter:
    """Count records by extension in database."""
    # Get all files and count in Python (simpler than complex SQL)
    result = subprocess.run(
        ['sqlite-utils', 'query', str(db_path), f'SELECT file FROM "{table}"'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"Error querying database: {result.stderr}")
        sys.exit(1)

    data = json.loads(result.stdout)
    counter = Counter()

    for row in data:
        ext = get_extension(row.get('file', ''))
        counter[ext] += 1

    return counter


def main():
    parser = argparse.ArgumentParser(
        description='Verify image descriptions import to database'
    )
    parser.add_argument(
        '--json-file',
        default='outputs/image_analysis.json',
        help='Path to JSON file (default: outputs/image_analysis.json)'
    )
    parser.add_argument(
        '--database',
        default='database/mediameta.db',
        help='Path to SQLite database (default: database/mediameta.db)'
    )
    parser.add_argument(
        '--table',
        default='image_description',
        help='Table name (default: image_description)'
    )

    args = parser.parse_args()

    json_path = Path(args.json_file)
    db_path = Path(args.database)

    # Check paths
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)

    # Count records
    print(f"Counting records in JSON: {json_path}")
    json_counts, skipped_count = count_json_by_extension(json_path)
    json_total = sum(json_counts.values())

    print(f"Counting records in database: {db_path}")
    db_counts = count_database_by_extension(db_path, args.table)
    db_total = sum(db_counts.values())

    # Get all extensions
    all_extensions = sorted(set(json_counts.keys()) | set(db_counts.keys()))

    # Print comparison table
    print()
    print(f"{'Extension':<10} | {'JSON':>8} | {'Database':>8} | Status")
    print("-" * 45)

    all_match = True
    for ext in all_extensions:
        json_count = json_counts.get(ext, 0)
        db_count = db_counts.get(ext, 0)

        if json_count == db_count:
            status = "✓"
        elif db_count < json_count:
            status = f"⚠ Missing {json_count - db_count}"
            all_match = False
        else:
            status = f"⚠ Extra {db_count - json_count}"
            all_match = False

        print(f"{ext:<10} | {json_count:>8,} | {db_count:>8,} | {status}")

    print("-" * 45)
    print(f"{'TOTAL':<10} | {json_total:>8,} | {db_total:>8,} |")

    if skipped_count > 0:
        print(f"\nNote: {skipped_count:,} 'Skipped for now' records excluded from JSON count")

    # Summary
    print()
    if all_match and json_total == db_total:
        print("✓ All records verified - JSON and database match!")
        return 0
    else:
        print("⚠ Discrepancy detected - some records may not have been imported")
        print("  Run: python scripts/import_image_descriptions.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())

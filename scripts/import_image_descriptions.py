#!/usr/bin/env python3
"""
Import image descriptions from JSON to SQLite database.

Uses sqlite-utils upsert to safely update/insert records.
Can be run multiple times as new data arrives.

Usage:
    python scripts/import_image_descriptions.py
    python scripts/import_image_descriptions.py --json-file outputs/image_analysis.json
    python scripts/import_image_descriptions.py --dry-run
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_json(json_path: Path) -> tuple[list, str]:
    """
    Load and validate JSON file.
    Returns (data, error_message)
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            return [], "JSON root is not an array"

        return data, ""
    except json.JSONDecodeError as e:
        return [], f"Invalid JSON: {e}"
    except Exception as e:
        return [], f"Error reading file: {e}"


def get_existing_files(db_path: Path, table_name: str) -> set:
    """Get set of file values already in the database."""
    try:
        result = subprocess.run(
            ['sqlite-utils', 'query', str(db_path),
             f'SELECT file FROM "{table_name}"'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {row['file'] for row in data}
    except Exception:
        pass
    return set()


def insert_records(db_path: Path, table_name: str, records: list) -> tuple[bool, str]:
    """
    Insert new records into SQLite table.
    Returns (success, message)
    """
    if not records:
        return True, "No new records to insert"

    # Pass records via stdin as JSON
    result = subprocess.run(
        ['sqlite-utils', 'insert', str(db_path), table_name, '-', '--pk', 'file'],
        input=json.dumps(records),
        capture_output=True, text=True
    )

    if result.returncode == 0:
        return True, "Insert completed successfully"
    else:
        return False, f"Insert failed: {result.stderr}"


def main():
    parser = argparse.ArgumentParser(
        description='Import image descriptions from JSON to SQLite'
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
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate JSON without importing'
    )

    args = parser.parse_args()

    json_path = Path(args.json_file)
    db_path = Path(args.database)
    table_name = args.table

    # Check paths exist
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)

    # Load JSON
    print(f"Loading JSON file: {json_path}")
    all_records, error = load_json(json_path)

    if error:
        print(f"Error: {error}")
        print("The JSON file may be mid-write. Try again in a moment.")
        sys.exit(1)

    print(f"JSON valid: {len(all_records)} records found")

    # Get existing files from database
    print(f"Checking existing records in database...")
    existing_files = get_existing_files(db_path, table_name)
    print(f"Table '{table_name}' current rows: {len(existing_files)}")

    # Filter to only new records
    new_records = [r for r in all_records if r.get('file') not in existing_files]
    print(f"New records to insert: {len(new_records)}")

    if args.dry_run:
        print("Dry run - no changes made")
        sys.exit(0)

    if not new_records:
        print()
        print("WARNING: No new records to insert!")
        print("  If the batch process is running, this may indicate:")
        print("  - Batch is still processing (not yet written to JSON)")
        print("  - Batch process has stalled")
        print("  Check logs: tail -20 logs/batch_orchestrator_*.log")
        sys.exit(0)

    # Insert only new records
    print(f"Inserting {len(new_records)} new records...")
    success, message = insert_records(db_path, table_name, new_records)

    if not success:
        print(f"Error: {message}")
        sys.exit(1)

    print(f"Done!")
    print(f"  Records in JSON: {len(all_records)}")
    print(f"  Previously imported: {len(existing_files)}")
    print(f"  New rows added: {len(new_records)}")


if __name__ == '__main__':
    main()

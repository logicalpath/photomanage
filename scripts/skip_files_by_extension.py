#!/usr/bin/env python3
"""
Skip files by extension - add placeholder entries to defer processing.

Adds placeholder records to image_analysis.json and progress file so
batch processing skips these files. Can be undone later.

Usage:
    python scripts/skip_files_by_extension.py --ext NEF
    python scripts/skip_files_by_extension.py --ext NEF --dry-run
    python scripts/skip_files_by_extension.py --ext NEF --undo
"""

import argparse
import json
import sys
from pathlib import Path


PROGRESS_FILE = "photo_descriptions_progress.txt"
JSON_FILE = "outputs/image_analysis.json"
SKIP_DESCRIPTION = "Skipped for now"
SKIP_MODEL = "skipped"


def load_progress_file() -> set:
    """Load processed files from progress file."""
    path = Path(PROGRESS_FILE)
    if not path.exists():
        return set()
    with open(path, 'r') as f:
        return set(line.strip() for line in f if line.strip())


def load_json_file() -> list:
    """Load existing JSON data."""
    path = Path(JSON_FILE)
    if not path.exists():
        return []
    with open(path, 'r') as f:
        return json.load(f)


def find_files_by_extension(directory: Path, extension: str) -> list:
    """Find all files with given extension in directory."""
    ext_upper = extension.upper().lstrip('.')
    ext_lower = extension.lower().lstrip('.')

    files = []
    for f in directory.rglob('*'):
        if f.is_file() and f.suffix.upper().lstrip('.') == ext_upper:
            files.append(f)

    return sorted(files)


def skip_files(directory: str, extension: str, dry_run: bool = False) -> int:
    """
    Add placeholder entries for files with given extension.

    Returns count of files skipped.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    # Find all files with extension
    all_files = find_files_by_extension(dir_path, extension)
    print(f"Found {len(all_files):,} {extension.upper()} files in {directory}")

    # Load current progress
    progress = load_progress_file()
    print(f"Already in progress file: {len(progress):,} files")

    # Find unprocessed files
    unprocessed = []
    for f in all_files:
        rel_path = str(f.relative_to(dir_path))
        if rel_path not in progress:
            unprocessed.append(rel_path)

    print(f"Unprocessed {extension.upper()} files: {len(unprocessed):,}")

    if not unprocessed:
        print("Nothing to skip!")
        return 0

    if dry_run:
        print(f"\nDry run - would skip {len(unprocessed):,} files")
        print("Sample files:")
        for f in unprocessed[:5]:
            print(f"  {f}")
        if len(unprocessed) > 5:
            print(f"  ... and {len(unprocessed) - 5} more")
        return len(unprocessed)

    # Load existing JSON
    json_data = load_json_file()
    print(f"Existing JSON records: {len(json_data):,}")

    # Create placeholder records
    new_records = []
    for rel_path in unprocessed:
        new_records.append({
            "file": f"./{rel_path}",
            "description": SKIP_DESCRIPTION,
            "model": SKIP_MODEL,
            "generation_time_seconds": 0.00,
            "error": False
        })

    # Append to JSON
    json_data.extend(new_records)
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"Added {len(new_records):,} placeholder records to JSON")

    # Append to progress file
    with open(PROGRESS_FILE, 'a') as f:
        for rel_path in unprocessed:
            f.write(f"{rel_path}\n")
    print(f"Added {len(unprocessed):,} entries to progress file")

    print(f"\nSkipped {len(unprocessed):,} {extension.upper()} files")
    return len(unprocessed)


def undo_skip(extension: str, dry_run: bool = False) -> int:
    """
    Remove placeholder entries for files with given extension.

    Returns count of files unskipped.
    """
    ext_upper = extension.upper().lstrip('.')

    # Load JSON and find skipped entries
    json_data = load_json_file()
    skipped = []
    kept = []

    for record in json_data:
        file_path = record.get('file', '')
        is_skipped = (
            record.get('description') == SKIP_DESCRIPTION and
            record.get('model') == SKIP_MODEL and
            file_path.upper().endswith(f'.{ext_upper}')
        )
        if is_skipped:
            skipped.append(file_path)
        else:
            kept.append(record)

    print(f"Found {len(skipped):,} skipped {ext_upper} entries in JSON")

    if not skipped:
        print("Nothing to undo!")
        return 0

    if dry_run:
        print(f"\nDry run - would remove {len(skipped):,} entries")
        return len(skipped)

    # Update JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(kept, f, indent=2, ensure_ascii=False)
    print(f"Removed {len(skipped):,} placeholder records from JSON")

    # Update progress file
    progress = load_progress_file()
    # Remove the skipped files from progress
    skipped_rel_paths = set(p.lstrip('./') for p in skipped)
    remaining = progress - skipped_rel_paths

    with open(PROGRESS_FILE, 'w') as f:
        for rel_path in sorted(remaining):
            f.write(f"{rel_path}\n")
    print(f"Removed {len(skipped_rel_paths):,} entries from progress file")

    print(f"\nUndid skip for {len(skipped):,} {ext_upper} files")
    return len(skipped)


def main():
    parser = argparse.ArgumentParser(
        description='Skip files by extension - add placeholder entries'
    )
    parser.add_argument(
        '--ext',
        required=True,
        help='File extension to skip (e.g., NEF, HEIC)'
    )
    parser.add_argument(
        '--directory',
        default='database/512x512',
        help='Source directory (default: database/512x512)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without making changes'
    )
    parser.add_argument(
        '--undo',
        action='store_true',
        help='Remove placeholder entries (undo skip)'
    )

    args = parser.parse_args()

    if args.undo:
        undo_skip(args.ext, args.dry_run)
    else:
        skip_files(args.directory, args.ext, args.dry_run)


if __name__ == '__main__':
    main()

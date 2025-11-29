#!/usr/bin/env python3
"""
Find files that were processed but missing descriptions.

Compares photo_descriptions_progress.txt (source of truth for processed files)
against outputs/image_analysis.json to find gaps caused by interrupted batches.

Usage:
    python scripts/find_missing_descriptions.py
    python scripts/find_missing_descriptions.py --fix  # Remove missing from progress file
"""

import argparse
import json
import sys
from pathlib import Path


def load_progress_file(path: Path) -> set:
    """Load processed files from progress file."""
    if not path.exists():
        return set()
    with open(path, 'r') as f:
        return set(line.strip() for line in f if line.strip())


def load_json_files(path: Path) -> set:
    """Load file paths from JSON output."""
    if not path.exists():
        return set()
    with open(path, 'r') as f:
        data = json.load(f)
    # Strip leading './' to match progress file format
    return set(r['file'].lstrip('./') for r in data)


def main():
    parser = argparse.ArgumentParser(
        description='Find files missing descriptions due to interrupted batches'
    )
    parser.add_argument(
        '--progress-file',
        default='photo_descriptions_progress.txt',
        help='Path to progress file (default: photo_descriptions_progress.txt)'
    )
    parser.add_argument(
        '--json-file',
        default='outputs/image_analysis.json',
        help='Path to JSON output (default: outputs/image_analysis.json)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Remove missing files from progress file so they get reprocessed'
    )
    parser.add_argument(
        '--output',
        help='Write missing files to this file (one per line)'
    )

    args = parser.parse_args()

    progress_path = Path(args.progress_file)
    json_path = Path(args.json_file)

    # Check files exist
    if not progress_path.exists():
        print(f"Error: Progress file not found: {progress_path}")
        sys.exit(1)

    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    # Load both sources
    progress_files = load_progress_file(progress_path)
    json_files = load_json_files(json_path)

    # Find missing (in progress but not in JSON)
    missing = progress_files - json_files

    # Report
    print(f"Progress file: {len(progress_files)} files")
    print(f"JSON file:     {len(json_files)} files")
    print(f"Missing:       {len(missing)} files")

    if not missing:
        print("\nNo missing descriptions. All synced!")
        sys.exit(0)

    print(f"\nMissing files:")
    for f in sorted(missing)[:20]:
        print(f"  {f}")
    if len(missing) > 20:
        print(f"  ... and {len(missing) - 20} more")

    # Write to output file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            for file in sorted(missing):
                f.write(f"{file}\n")
        print(f"\nMissing files written to: {output_path}")

    # Fix by removing from progress file
    if args.fix:
        print(f"\nRemoving {len(missing)} entries from progress file...")
        remaining = progress_files - missing
        with open(progress_path, 'w') as f:
            for file in sorted(remaining):
                f.write(f"{file}\n")
        print(f"Progress file updated: {len(remaining)} entries")
        print("These files will be reprocessed on next batch run.")
    else:
        print(f"\nTo fix, run: python scripts/find_missing_descriptions.py --fix")


if __name__ == '__main__':
    main()

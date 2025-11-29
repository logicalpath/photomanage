#!/usr/bin/env python3
"""
Analyze image processing times by file type and model.

Shows median, average, and standard deviation for processing times,
broken down by file extension and model.

Usage:
    python scripts/analyze_processing_times.py
    python scripts/analyze_processing_times.py --ext NEF
    python scripts/analyze_processing_times.py --ext NEF --ext JPG
    python scripts/analyze_processing_times.py --all
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def load_json(json_path: Path) -> list:
    """Load JSON data."""
    with open(json_path, 'r') as f:
        return json.load(f)


def median(lst: list) -> float:
    """Calculate median of a list."""
    if not lst:
        return 0
    s = sorted(lst)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2


def std_dev(lst: list) -> float:
    """Calculate standard deviation of a list."""
    if not lst:
        return 0
    avg = sum(lst) / len(lst)
    variance = sum((x - avg) ** 2 for x in lst) / len(lst)
    return math.sqrt(variance)


def analyze_times(data: list, extensions: list = None) -> dict:
    """
    Analyze processing times by extension and model.

    Args:
        data: List of records from JSON
        extensions: List of extensions to filter (None = all)

    Returns:
        Dict with analysis results
    """
    # Group times by extension and model
    by_ext = defaultdict(lambda: defaultdict(list))

    for r in data:
        if r.get('generation_time_seconds') and not r.get('error'):
            ext = r['file'].rsplit('.', 1)[-1].upper()
            if extensions is None or ext in extensions:
                t = r['generation_time_seconds']
                model = r.get('model', 'unknown')
                by_ext[ext][model].append(t)
                by_ext[ext]['_all'].append(t)

    return by_ext


def print_stats(times: list, label: str, indent: int = 0):
    """Print statistics for a list of times."""
    prefix = ' ' * indent
    if not times:
        print(f"{prefix}{label}: No data")
        return

    avg = sum(times) / len(times)
    med = median(times)
    sd = std_dev(times)

    print(f"{prefix}{label}:")
    print(f"{prefix}  Count:  {len(times):,}")
    print(f"{prefix}  Median: {med:.2f}s")
    print(f"{prefix}  Avg:    {avg:.2f}s")
    print(f"{prefix}  StdDev: {sd:.2f}s")
    print(f"{prefix}  Range:  {min(times):.2f}s - {max(times):.2f}s")


def print_table(by_ext: dict):
    """Print a summary table."""
    print(f"\n{'Extension':<10} {'Model':<12} {'Count':>7} {'Median':>9} {'Avg':>9} {'StdDev':>9}")
    print("-" * 60)

    for ext in sorted(by_ext.keys()):
        models = by_ext[ext]
        # Overall for this extension
        all_times = models['_all']
        if all_times:
            avg = sum(all_times) / len(all_times)
            print(f"{ext:<10} {'(all)':<12} {len(all_times):>7,} {median(all_times):>8.2f}s {avg:>8.2f}s {std_dev(all_times):>8.2f}s")

        # By model
        for model in sorted(m for m in models.keys() if m != '_all'):
            times = models[model]
            if times:
                avg = sum(times) / len(times)
                print(f"{'':<10} {model:<12} {len(times):>7,} {median(times):>8.2f}s {avg:>8.2f}s {std_dev(times):>8.2f}s")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze image processing times by file type and model'
    )
    parser.add_argument(
        '--json-file',
        default='outputs/image_analysis.json',
        help='Path to JSON file (default: outputs/image_analysis.json)'
    )
    parser.add_argument(
        '--ext',
        action='append',
        dest='extensions',
        help='File extension to analyze (can specify multiple, e.g., --ext NEF --ext JPG)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Show all extensions'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed output instead of table'
    )

    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    # Load data
    data = load_json(json_path)
    print(f"Loaded {len(data):,} records from {json_path}")

    # Normalize extensions
    extensions = None
    if args.extensions:
        extensions = [e.upper().lstrip('.') for e in args.extensions]
    elif not args.all:
        # Default to NEF if no extension specified
        extensions = ['NEF']
        print("(Defaulting to NEF files. Use --all for all extensions or --ext to specify)")

    # Analyze
    by_ext = analyze_times(data, extensions)

    if not by_ext:
        print("No matching records found")
        sys.exit(0)

    # Output
    if args.detailed:
        print("\n" + "=" * 50)
        print("PROCESSING TIME ANALYSIS")
        print("=" * 50)

        for ext in sorted(by_ext.keys()):
            print(f"\n{ext} Files:")
            print("-" * 40)

            models = by_ext[ext]
            print_stats(models['_all'], "Overall", indent=2)

            print()
            for model in sorted(m for m in models.keys() if m != '_all'):
                print_stats(models[model], model, indent=2)
                print()
    else:
        print_table(by_ext)


if __name__ == '__main__':
    main()

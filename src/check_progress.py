#!/usr/bin/env python3
"""
Quick Progress Checker for Image Description Generation

Shows current progress, estimated time remaining, and recent status.

Usage:
    python src/check_progress.py [directory]

Example:
    python src/check_progress.py database/512x512
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


PROGRESS_FILE = "photo_descriptions_progress.txt"


def count_files_in_directory(directory: str) -> int:
    """Count total files in directory (excluding hidden files)."""
    count = 0
    skip_files = {'.ds_store', 'thumbs.db', '.gitignore', '.gitkeep'}
    directory_path = Path(directory)

    for path in directory_path.rglob('*'):
        if path.is_file():
            if not path.name.startswith('.') and path.name.lower() not in skip_files:
                count += 1
    return count


def get_progress_info():
    """Get information from progress file."""
    if not os.path.exists(PROGRESS_FILE):
        return {
            'completed_count': 0,
            'last_file': None,
            'last_modified': None,
            'files': []
        }

    with open(PROGRESS_FILE, 'r') as f:
        files = [line.strip() for line in f if line.strip()]

    if not files:
        return {
            'completed_count': 0,
            'last_file': None,
            'last_modified': None,
            'files': []
        }

    # Get file modification time
    last_modified = datetime.fromtimestamp(os.path.getmtime(PROGRESS_FILE))

    return {
        'completed_count': len(files),
        'last_file': files[-1] if files else None,
        'last_modified': last_modified,
        'files': files
    }


def get_recent_errors():
    """Check recent log files for errors."""
    log_dir = Path("logs")
    if not log_dir.exists():
        return 0

    error_count = 0
    # Get most recent log file
    log_files = sorted(log_dir.glob("batch_orchestrator_*.log"), reverse=True)

    if not log_files:
        return 0

    # Check most recent log for errors
    recent_log = log_files[0]
    try:
        with open(recent_log, 'r') as f:
            for line in f:
                if 'ERROR' in line or 'failed' in line.lower():
                    error_count += 1
    except Exception:
        pass

    return error_count


def estimate_time_remaining(completed: int, total: int, last_modified: datetime) -> tuple:
    """
    Estimate time remaining based on recent progress.

    Returns:
        Tuple of (hours_remaining, rate_per_hour, is_stale)
    """
    if completed == 0 or last_modified is None:
        return None, None, False

    # Check if processing is stale (no progress in 10 minutes)
    time_since_update = datetime.now() - last_modified
    is_stale = time_since_update > timedelta(minutes=10)

    if is_stale:
        return None, None, True

    # Calculate rate based on time since last update
    # Assume the last file was just completed
    # This is a rough estimate - real rate tracking would need timestamps per file
    hours_elapsed = time_since_update.total_seconds() / 3600

    # For a better estimate, assume average processing time
    # Check outputs directory for recent timing data
    avg_time_per_image = estimate_avg_time_per_image()

    if avg_time_per_image:
        remaining = total - completed
        hours_remaining = (remaining * avg_time_per_image) / 3600
        rate_per_hour = 3600 / avg_time_per_image
    else:
        # Fallback: very rough estimate
        # Assume 1 image per 10 seconds (360 per hour)
        rate_per_hour = 360
        remaining = total - completed
        hours_remaining = remaining / rate_per_hour

    return hours_remaining, rate_per_hour, False


def estimate_avg_time_per_image() -> float:
    """
    Estimate average time per image from recent output files.

    Returns:
        Average seconds per image, or None if unable to estimate
    """
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return None

    # Get most recent output file
    output_files = sorted(outputs_dir.glob("image_analysis_*.json"), reverse=True)
    if not output_files:
        return None

    try:
        import json
        with open(output_files[0], 'r') as f:
            data = json.load(f)

        if not data:
            return None

        # Calculate average from generation_time_seconds
        times = [
            item['generation_time_seconds']
            for item in data
            if item.get('generation_time_seconds') is not None
        ]

        if times:
            return sum(times) / len(times)

    except Exception:
        pass

    return None


def format_timedelta(hours: float) -> str:
    """Format hours into human-readable string."""
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes} minutes"
    elif hours < 24:
        return f"{hours:.1f} hours"
    else:
        days = int(hours / 24)
        remaining_hours = hours % 24
        return f"{days} days, {remaining_hours:.1f} hours"


def main():
    parser = argparse.ArgumentParser(description="Check image description progress")
    parser.add_argument(
        'directory',
        nargs='?',
        default='database/512x512',
        help='Directory containing images (default: database/512x512)'
    )
    args = parser.parse_args()

    # Get total file count
    if not os.path.isdir(args.directory):
        print(f"Error: Directory not found: {args.directory}")
        sys.exit(1)

    print(f"Counting files in {args.directory}...")
    total_files = count_files_in_directory(args.directory)

    # Get progress info
    progress = get_progress_info()
    completed = progress['completed_count']
    remaining = total_files - completed
    percent = (completed / total_files * 100) if total_files > 0 else 0

    # Print status
    print("\n" + "=" * 60)
    print("IMAGE DESCRIPTION PROGRESS")
    print("=" * 60)
    print(f"Completed:  {completed:,} / {total_files:,} ({percent:.1f}%)")
    print(f"Remaining:  {remaining:,}")

    # Progress bar
    bar_width = 40
    filled = int(bar_width * percent / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"Progress:   [{bar}]")

    # Time estimates
    if progress['last_modified']:
        time_since = datetime.now() - progress['last_modified']
        minutes_since = int(time_since.total_seconds() / 60)

        if minutes_since < 60:
            print(f"Last update: {minutes_since} minutes ago")
        else:
            hours_since = minutes_since / 60
            print(f"Last update: {hours_since:.1f} hours ago")

        hours_remaining, rate, is_stale = estimate_time_remaining(
            completed, total_files, progress['last_modified']
        )

        if is_stale:
            print("Status:     ⚠️  Processing appears to be stopped")
        elif hours_remaining is not None:
            print(f"Est. time:  {format_timedelta(hours_remaining)} remaining")
            print(f"Rate:       ~{rate:.0f} images/hour")
        else:
            print("Status:     Processing started")
    else:
        print("Status:     Not started")

    # Last file processed
    if progress['last_file']:
        print(f"Last file:  {progress['last_file']}")

    # Check for errors
    error_count = get_recent_errors()
    if error_count > 0:
        print(f"Errors:     ⚠️  {error_count} errors in recent log")

    print("=" * 60)

    # Show log file location
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = sorted(log_dir.glob("batch_orchestrator_*.log"), reverse=True)
        if log_files:
            print(f"\nMost recent log: {log_files[0]}")
            print(f"View live: tail -f {log_files[0]}")

    print()


if __name__ == "__main__":
    main()

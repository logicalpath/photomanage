#!/usr/bin/env python3
"""
Detailed Progress Summary for Image Description Generation

Shows comprehensive statistics including:
- Overall progress
- Success/error rates
- Batch timing statistics
- Memory usage trends (from logs)
- Recent errors

Usage:
    python src/progress_summary.py
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROGRESS_FILE = "photo_descriptions_progress.txt"


def get_output_files():
    """Get all JSON output files sorted by timestamp."""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return []

    return sorted(outputs_dir.glob("image_analysis_*.json"))


def analyze_outputs():
    """Analyze all output files for statistics."""
    output_files = get_output_files()

    if not output_files:
        return None

    total_processed = 0
    total_successful = 0
    total_failed = 0
    total_time = 0.0
    generation_times = []
    errors_by_type = defaultdict(int)

    for output_file in output_files:
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)

            for item in data:
                total_processed += 1

                if item.get('error', False):
                    total_failed += 1
                    # Categorize error
                    error_msg = item.get('description', '')
                    if 'memory' in error_msg.lower():
                        errors_by_type['Memory Error'] += 1
                    elif 'timeout' in error_msg.lower():
                        errors_by_type['Timeout'] += 1
                    else:
                        errors_by_type['Other Error'] += 1
                else:
                    total_successful += 1
                    gen_time = item.get('generation_time_seconds')
                    if gen_time:
                        total_time += gen_time
                        generation_times.append(gen_time)

        except Exception as e:
            print(f"Warning: Could not read {output_file}: {e}")

    if not generation_times:
        return None

    # Calculate statistics
    avg_time = sum(generation_times) / len(generation_times)
    min_time = min(generation_times)
    max_time = max(generation_times)

    # Calculate median
    sorted_times = sorted(generation_times)
    mid = len(sorted_times) // 2
    median_time = sorted_times[mid] if len(sorted_times) % 2 else \
        (sorted_times[mid - 1] + sorted_times[mid]) / 2

    return {
        'total_processed': total_processed,
        'total_successful': total_successful,
        'total_failed': total_failed,
        'success_rate': (total_successful / total_processed * 100) if total_processed > 0 else 0,
        'avg_time': avg_time,
        'median_time': median_time,
        'min_time': min_time,
        'max_time': max_time,
        'errors_by_type': dict(errors_by_type)
    }


def analyze_logs():
    """Analyze log files for batch statistics and memory usage."""
    log_dir = Path("logs")
    if not log_dir.exists():
        return None

    log_files = sorted(log_dir.glob("batch_orchestrator_*.log"))
    if not log_files:
        return None

    batch_count = 0
    memory_readings = []
    cpu_readings = []
    errors = []

    # Regex patterns
    batch_pattern = re.compile(r'Starting batch (\d+)')
    memory_pattern = re.compile(r'Memory: ([\d.]+)%')
    cpu_pattern = re.compile(r'CPU: ([\d.]+)%')
    error_pattern = re.compile(r'ERROR.*?- (.*)')

    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    # Count batches
                    if 'Starting batch' in line:
                        batch_count += 1

                    # Extract memory usage
                    mem_match = memory_pattern.search(line)
                    if mem_match:
                        memory_readings.append(float(mem_match.group(1)))

                    # Extract CPU usage
                    cpu_match = cpu_pattern.search(line)
                    if cpu_match:
                        cpu_readings.append(float(cpu_match.group(1)))

                    # Collect errors
                    if 'ERROR' in line:
                        error_match = error_pattern.search(line)
                        if error_match:
                            errors.append(error_match.group(1).strip())

        except Exception as e:
            print(f"Warning: Could not read {log_file}: {e}")

    result = {
        'batch_count': batch_count,
        'recent_errors': errors[-10:] if errors else []  # Last 10 errors
    }

    if memory_readings:
        result['memory'] = {
            'avg': sum(memory_readings) / len(memory_readings),
            'min': min(memory_readings),
            'max': max(memory_readings),
            'current': memory_readings[-1] if memory_readings else None
        }

    if cpu_readings:
        result['cpu'] = {
            'avg': sum(cpu_readings) / len(cpu_readings),
            'max': max(cpu_readings)
        }

    return result


def get_progress_count():
    """Get count of completed files from progress file."""
    if not os.path.exists(PROGRESS_FILE):
        return 0

    with open(PROGRESS_FILE, 'r') as f:
        return sum(1 for line in f if line.strip())


def main():
    print("\n" + "=" * 70)
    print("DETAILED PROGRESS SUMMARY")
    print("=" * 70)

    # Overall progress
    completed = get_progress_count()
    print(f"\nTotal files processed: {completed:,}")

    # Output file analysis
    print("\n" + "-" * 70)
    print("OUTPUT FILE ANALYSIS")
    print("-" * 70)

    output_stats = analyze_outputs()
    if output_stats:
        print(f"Total in outputs:     {output_stats['total_processed']:,}")
        print(f"Successful:           {output_stats['total_successful']:,}")
        print(f"Failed:               {output_stats['total_failed']}")
        print(f"Success rate:         {output_stats['success_rate']:.1f}%")

        print(f"\nGeneration time per image:")
        print(f"  Average:            {output_stats['avg_time']:.2f}s")
        print(f"  Median:             {output_stats['median_time']:.2f}s")
        print(f"  Range:              {output_stats['min_time']:.2f}s - {output_stats['max_time']:.2f}s")

        if output_stats['errors_by_type']:
            print(f"\nError breakdown:")
            for error_type, count in output_stats['errors_by_type'].items():
                print(f"  {error_type}: {count}")
    else:
        print("No output files found")

    # Log file analysis
    print("\n" + "-" * 70)
    print("LOG FILE ANALYSIS")
    print("-" * 70)

    log_stats = analyze_logs()
    if log_stats:
        print(f"Total batches run:    {log_stats['batch_count']}")

        if 'memory' in log_stats:
            mem = log_stats['memory']
            print(f"\nMemory usage:")
            print(f"  Average:            {mem['avg']:.1f}%")
            print(f"  Range:              {mem['min']:.1f}% - {mem['max']:.1f}%")
            if mem['current']:
                print(f"  Most recent:        {mem['current']:.1f}%")

        if 'cpu' in log_stats:
            cpu = log_stats['cpu']
            print(f"\nCPU usage:")
            print(f"  Average:            {cpu['avg']:.1f}%")
            print(f"  Max:                {cpu['max']:.1f}%")

        if log_stats['recent_errors']:
            print(f"\nRecent errors ({len(log_stats['recent_errors'])}):")
            for i, error in enumerate(log_stats['recent_errors'][-5:], 1):
                # Truncate long errors
                error_display = error[:80] + "..." if len(error) > 80 else error
                print(f"  {i}. {error_display}")
    else:
        print("No log files found")

    # File locations
    print("\n" + "-" * 70)
    print("FILES")
    print("-" * 70)
    print(f"Progress file:        {PROGRESS_FILE}")

    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        output_files = list(outputs_dir.glob("image_analysis_*.json"))
        print(f"Output files:         {len(output_files)} files in outputs/")

    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("batch_orchestrator_*.log"))
        print(f"Log files:            {len(log_files)} files in logs/")

        if log_files:
            most_recent = sorted(log_files, reverse=True)[0]
            print(f"Most recent log:      {most_recent}")

    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

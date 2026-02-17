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
    python src/progress_summary.py          # current session only
    python src/progress_summary.py --all    # all sessions
"""

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path


PROGRESS_FILE = "photo_descriptions_progress.txt"


def get_output_files():
    """Get all JSON output files sorted by timestamp."""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return []

    return sorted(outputs_dir.glob("image_analysis*.json"))


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
    prompt_tps_readings = []
    generation_tps_readings = []
    prompt_token_counts = []
    generation_token_counts = []
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

                    # Collect GPU throughput metrics
                    if item.get('prompt_tps'):
                        prompt_tps_readings.append(item['prompt_tps'])
                    if item.get('generation_tps'):
                        generation_tps_readings.append(item['generation_tps'])
                    if item.get('prompt_tokens'):
                        prompt_token_counts.append(item['prompt_tokens'])
                    if item.get('generation_tokens'):
                        generation_token_counts.append(item['generation_tokens'])

        except Exception as e:
            print(f"Warning: Could not read {output_file}: {e}")

    # Build GPU throughput stats
    gpu_stats = {}
    if prompt_tps_readings:
        gpu_stats['prompt_tps_avg'] = sum(prompt_tps_readings) / len(prompt_tps_readings)
        gpu_stats['prompt_tps_min'] = min(prompt_tps_readings)
        gpu_stats['prompt_tps_max'] = max(prompt_tps_readings)
    if generation_tps_readings:
        gpu_stats['generation_tps_avg'] = sum(generation_tps_readings) / len(generation_tps_readings)
        gpu_stats['generation_tps_min'] = min(generation_tps_readings)
        gpu_stats['generation_tps_max'] = max(generation_tps_readings)
    if prompt_token_counts:
        gpu_stats['prompt_tokens_avg'] = sum(prompt_token_counts) / len(prompt_token_counts)
    if generation_token_counts:
        gpu_stats['generation_tokens_avg'] = sum(generation_token_counts) / len(generation_token_counts)

    if not generation_times:
        # No successful generations with timing, but return failure stats
        return {
            'total_processed': total_processed,
            'total_successful': total_successful,
            'total_failed': total_failed,
            'success_rate': (total_successful / total_processed * 100) if total_processed > 0 else 0,
            'avg_time': None,
            'median_time': None,
            'min_time': None,
            'max_time': None,
            'errors_by_type': dict(errors_by_type),
            'gpu': gpu_stats if gpu_stats else None
        }

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
        'errors_by_type': dict(errors_by_type),
        'gpu': gpu_stats if gpu_stats else None
    }


def analyze_logs(all_logs=False):
    """Analyze log files for batch statistics and memory usage.

    Args:
        all_logs: If True, analyze all log files. Otherwise only the most recent.
    """
    log_dir = Path("logs")
    if not log_dir.exists():
        return None

    log_files = sorted(log_dir.glob("batch_orchestrator_*.log"))
    if not log_files:
        return None

    if all_logs:
        logs_to_analyze = log_files
    else:
        logs_to_analyze = [log_files[-1]]

    batch_count = 0
    memory_readings = []
    cpu_readings = []
    gpu_tps_readings = []
    errors = []

    # Regex patterns
    memory_pattern = re.compile(r'Memory: ([\d.]+)%')
    cpu_pattern = re.compile(r'CPU: ([\d.]+)%')
    gpu_tps_pattern = re.compile(r'GPU Throughput - Batch avg: ([\d.]+) tokens/sec')
    batch_failed_pattern = re.compile(r'Batch (\d+) failed with error code (\d+)')

    for log_file in logs_to_analyze:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
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

                # Extract GPU throughput
                gpu_match = gpu_tps_pattern.search(line)
                if gpu_match:
                    gpu_tps_readings.append(float(gpu_match.group(1)))

                # Collect errors: combine "Batch N failed" with the error detail
                batch_match = batch_failed_pattern.search(line)
                if batch_match:
                    batch_num = batch_match.group(1)
                    error_code = batch_match.group(2)
                    # Look ahead for the error detail (skip "Error output:" line)
                    detail = ""
                    for j in range(i + 1, min(i + 3, len(lines))):
                        next_line = lines[j].strip()
                        if 'Error output' in next_line:
                            continue
                        if next_line and 'BatchOrchestrator' not in next_line:
                            detail = next_line
                            break
                    if detail:
                        errors.append(f"Batch {batch_num} (exit {error_code}): {detail}")
                    else:
                        errors.append(f"Batch {batch_num} (exit {error_code})")

        except Exception as e:
            print(f"Warning: Could not read {log_file}: {e}")

    log_label = f"{len(logs_to_analyze)} log files" if all_logs else logs_to_analyze[0].name
    result = {
        'batch_count': batch_count,
        'log_file': log_label,
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

    if gpu_tps_readings:
        result['gpu_tps'] = {
            'avg': sum(gpu_tps_readings) / len(gpu_tps_readings),
            'min': min(gpu_tps_readings),
            'max': max(gpu_tps_readings)
        }

    return result


def get_progress_count():
    """Get count of completed files from progress file."""
    if not os.path.exists(PROGRESS_FILE):
        return 0

    with open(PROGRESS_FILE, 'r') as f:
        return sum(1 for line in f if line.strip())


def main():
    parser = argparse.ArgumentParser(description="Progress summary for image description generation")
    parser.add_argument("--all", action="store_true",
                        help="Analyze all log files instead of just the current session")
    args = parser.parse_args()

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
        print(f"Success rate:         {output_stats['success_rate']:.2f}%")

        if (
            output_stats['avg_time'] is not None and
            output_stats['median_time'] is not None and
            output_stats['min_time'] is not None and
            output_stats['max_time'] is not None
        ):
            print(f"\nGeneration time per image:")
            print(f"  Average:            {output_stats['avg_time']:.2f}s")
            print(f"  Median:             {output_stats['median_time']:.2f}s")
            print(f"  Range:              {output_stats['min_time']:.2f}s - {output_stats['max_time']:.2f}s")
        else:
            print("\nGeneration time per image:")
            print("  Timing data unavailable.")

        if output_stats.get('gpu'):
            gpu = output_stats['gpu']
            print(f"\nGPU throughput (MLX):")
            if 'generation_tps_avg' in gpu:
                print(f"  Generation:         {gpu['generation_tps_avg']:.1f} tokens/sec avg "
                      f"({gpu['generation_tps_min']:.1f} - {gpu['generation_tps_max']:.1f})")
            if 'prompt_tps_avg' in gpu:
                print(f"  Prompt processing:  {gpu['prompt_tps_avg']:.1f} tokens/sec avg "
                      f"({gpu['prompt_tps_min']:.1f} - {gpu['prompt_tps_max']:.1f})")
            if 'prompt_tokens_avg' in gpu or 'generation_tokens_avg' in gpu:
                prompt_avg = gpu.get('prompt_tokens_avg', 0)
                gen_avg = gpu.get('generation_tokens_avg', 0)
                print(f"  Tokens per image:   {prompt_avg:.0f} prompt + {gen_avg:.0f} generation")

        if output_stats['errors_by_type']:
            print(f"\nError breakdown:")
            for error_type, count in output_stats['errors_by_type'].items():
                print(f"  {error_type}: {count}")
    else:
        print("No output files found")

    # Log file analysis
    print("\n" + "-" * 70)
    scope = "all sessions" if args.all else "current session"
    print(f"LOG FILE ANALYSIS ({scope})")
    print("-" * 70)

    log_stats = analyze_logs(all_logs=args.all)
    if log_stats:
        print(f"Log file:             {log_stats['log_file']}")
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

        if 'gpu_tps' in log_stats:
            gpu = log_stats['gpu_tps']
            print(f"\nGPU throughput (per-batch avg):")
            print(f"  Average:            {gpu['avg']:.1f} tokens/sec")
            print(f"  Range:              {gpu['min']:.1f} - {gpu['max']:.1f} tokens/sec")

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
        output_files = list(outputs_dir.glob("image_analysis*.json"))
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

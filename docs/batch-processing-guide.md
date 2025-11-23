# Batch Image Description Processing Guide

This guide covers the batch processing system for generating AI descriptions for large numbers of images (30,000+) reliably and efficiently.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Starting the Process](#starting-the-process)
- [Monitoring Progress](#monitoring-progress)
- [Stopping and Resuming](#stopping-and-resuming)
- [Running with Laptop Lid Closed](#running-with-laptop-lid-closed)
- [Understanding the Logs](#understanding-the-logs)
- [Troubleshooting](#troubleshooting)
- [System Requirements](#system-requirements)

## Overview

The batch processing system is designed to process tens of thousands of images without running into memory issues or requiring constant supervision.

### Key Features

- **Memory-safe**: Spawns a fresh Python process for each batch, automatically releasing all memory
- **Resume capability**: Can stop and resume at any time without losing progress
- **Failure recovery**: Built-in progress tracking skips already-processed images
- **Laptop-friendly**: Uses `caffeinate` to keep processing even with lid closed
- **Comprehensive monitoring**: Multiple tools to check progress and system health
- **Graceful shutdown**: Safely stops after completing the current batch

### Architecture

The system uses a **batch orchestrator** pattern:

```
run_batch_descriptions.sh
  └─> caffeinate (prevents sleep)
      └─> batch_orchestrator.py (main loop)
          ├─> Spawn: generate_descriptions.py (100 images)
          ├─> Process completes → ALL memory freed
          ├─> Cooldown: 30 seconds
          ├─> Check system resources
          └─> Repeat until done
```

**Why this works**: By spawning a NEW Python process for each batch, all memory (including any leaks from ML models) is automatically freed when the process exits. This allows the system to run indefinitely without memory issues.

## Installation

Before running the batch processor, ensure all dependencies are installed:

```bash
# Activate the pipenv environment
pipenv shell

# Install/update dependencies (includes psutil and click)
pipenv install
```

**Note**: The batch processing system requires `psutil` for system monitoring and `click` for command-line interfaces. These are included in the Pipfile.

## Quick Start

### 1. Start Processing

```bash
./scripts/run_batch_descriptions.sh
```

This processes images from `database/512x512` with default settings (100 images per batch, 30s cooldown).

### 2. Check Progress

```bash
# Quick status check
python src/check_progress.py

# Auto-refreshing dashboard (updates every 30s)
watch -n 30 'python src/check_progress.py'

# Detailed statistics
python src/progress_summary.py

# Live log tail
tail -f logs/orchestrator_console.log
```

### 3. Stop Processing

```bash
./scripts/stop_batch_descriptions.sh
```

The current batch will complete before stopping (safe shutdown).

## How It Works

### Process Isolation for Memory Management

Each batch runs in a completely separate Python process:

1. **Start batch**: Orchestrator spawns `generate_descriptions.py` as subprocess
2. **Process images**: Subprocess loads model, processes 100 images, saves results
3. **Exit**: Subprocess exits, operating system **automatically frees ALL memory**
4. **Cooldown**: Wait 30 seconds (allows system to stabilize)
5. **Repeat**: Start next batch with fresh memory

This approach eliminates memory leaks because the process is completely destroyed and recreated.

### Progress Tracking

Progress is tracked in `photo_descriptions_progress.txt`:
- One line per completed image (relative path)
- Updated after each successful image
- Used to skip already-processed images on resume
- Never deleted (allows infinite resume capability)

### File Organization

```
photomanage/
├── src/
│   ├── batch_orchestrator.py      # Main orchestrator
│   ├── generate_descriptions.py   # Per-batch processor
│   ├── check_progress.py          # Quick status
│   └── progress_summary.py        # Detailed stats
├── scripts/
│   ├── run_batch_descriptions.sh  # Start script
│   └── stop_batch_descriptions.sh # Stop script
├── logs/
│   ├── batch_orchestrator_*.log   # Detailed logs
│   └── orchestrator_console.log   # Console output
├── outputs/
│   └── image_analysis_*.json      # Description results
├── batch_orchestrator.pid         # Process ID (when running)
└── photo_descriptions_progress.txt # Progress tracking
```

## Starting the Process

### Basic Usage

```bash
./scripts/run_batch_descriptions.sh
```

### Custom Configuration

```bash
./scripts/run_batch_descriptions.sh <directory> <batch_size> <cooldown> <model>
```

**Parameters:**
- `directory`: Path to images (default: `database/512x512`)
- `batch_size`: Images per batch (default: `100`)
- `cooldown`: Seconds between batches (default: `30`)
- `model`: Model to use - `smolvlm` or `smolvlm2` (default: `smolvlm`)

**Examples:**

```bash
# Smaller batches with longer cooldown (more conservative)
./scripts/run_batch_descriptions.sh database/512x512 50 60

# Larger batches with shorter cooldown (faster, more aggressive)
./scripts/run_batch_descriptions.sh database/512x512 200 15

# Use SmolVLM2 model
./scripts/run_batch_descriptions.sh database/512x512 100 30 smolvlm2

# Different directory
./scripts/run_batch_descriptions.sh /path/to/images 100 30
```

### What Happens When You Start

1. Validates directory exists
2. Counts total files
3. Starts orchestrator with `caffeinate` (prevents sleep)
4. Saves process ID to `batch_orchestrator.pid`
5. Begins processing batches
6. Logs to `logs/` directory

## Monitoring Progress

### Quick Status Check

```bash
python src/check_progress.py
```

**Output:**
```
============================================================
IMAGE DESCRIPTION PROGRESS
============================================================
Completed:  5,430 / 31,841 (17.1%)
Remaining:  26,411
Progress:   [███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]
Last update: 2 minutes ago
Est. time:  14.2 hours remaining
Rate:       ~380 images/hour
Last file:  ./0/abc123.jpg
============================================================

Most recent log: logs/batch_orchestrator_20251123_143022.log
View live: tail -f logs/batch_orchestrator_20251123_143022.log
```

### Auto-Refreshing Dashboard

Uses the `watch` command to refresh status every 30 seconds:

```bash
watch -n 30 'python src/check_progress.py'
```

Press `Ctrl+C` to exit the watch view.

### Detailed Statistics

```bash
python src/progress_summary.py
```

**Output:**
```
======================================================================
DETAILED PROGRESS SUMMARY
======================================================================

Total files processed: 5,430

----------------------------------------------------------------------
OUTPUT FILE ANALYSIS
----------------------------------------------------------------------
Total in outputs:     5,430
Successful:           5,425
Failed:               5
Success rate:         99.9%

Generation time per image:
  Average:            8.2s
  Median:             7.8s
  Range:              3.1s - 45.2s

Error breakdown:
  Memory Error: 2
  Other Error: 3

----------------------------------------------------------------------
LOG FILE ANALYSIS
----------------------------------------------------------------------
Total batches run:    55

Memory usage:
  Average:            45.2%
  Range:              32.1% - 68.4%
  Most recent:        48.3%

CPU usage:
  Average:            78.5%
  Max:                95.2%

Recent errors (2):
  1. Error processing ./5/xyz789.jpg: Unsupported image format
  2. Timeout waiting for model response

----------------------------------------------------------------------
FILES
----------------------------------------------------------------------
Progress file:        photo_descriptions_progress.txt
Output files:         15 files in outputs/
Log files:            3 files in logs/
Most recent log:      logs/batch_orchestrator_20251123_143022.log
======================================================================
```

### Live Log Viewing

Watch the orchestrator work in real-time:

```bash
tail -f logs/orchestrator_console.log
```

**Example output:**
```
2025-11-23 14:32:15 - Progress: 5,400 / 31,841 (17.0%) - 26,441 remaining
2025-11-23 14:32:15 - Starting batch 55
2025-11-23 14:32:15 - System Stats - Memory: 48.3% used (15.2GB / 32.0GB), CPU: 82.1%
2025-11-23 14:32:15 - Running: python src/generate_descriptions.py database/512x512 100 --model smolvlm
2025-11-23 14:45:28 - Batch 55 completed successfully
2025-11-23 14:45:28 - Cooldown: waiting 30s before next batch...
```

Press `Ctrl+C` to stop viewing (doesn't stop the process).

## Stopping and Resuming

### Safe Stop

```bash
./scripts/stop_batch_descriptions.sh
```

**What happens:**
1. Sends interrupt signal to orchestrator
2. Current batch completes processing
3. Progress file is saved
4. Process exits gracefully
5. Shows final progress

**Important**: The stop is safe. All completed images are tracked, and you can resume anytime.

### Resume Processing

Just run the start script again:

```bash
./scripts/run_batch_descriptions.sh
```

The system will:
1. Read the progress file
2. Skip all already-processed images
3. Continue from where it left off

**You can stop and resume as many times as needed.**

### Check If Running

```bash
# Check for PID file
ls -l batch_orchestrator.pid

# Or check the process
ps aux | grep batch_orchestrator
```

## Running with Laptop Lid Closed

On macOS, closing the laptop lid normally puts the system to sleep and stops all processes. The start script uses `caffeinate` to prevent this.

### Requirements for Clamshell Mode

1. **Power adapter must be connected** (required for clamshell mode)
2. Run the start script (it automatically uses `caffeinate`)

### How It Works

The `caffeinate -i` command in the start script tells macOS:
- Keep system awake
- Continue running even with lid closed
- Don't sleep while processing

### Verification

After closing the lid:
1. Wait a few minutes
2. Open lid or SSH from another device
3. Check progress: `python src/check_progress.py`
4. Verify recent timestamp shows it kept running

### Alternative: External Display

If you prefer not to use caffeinate, you can:
1. Connect external display
2. Connect power adapter
3. Close lid (MacBook enters clamshell mode automatically)
4. Processing continues on external display

## Understanding the Logs

### Log Locations

- **`logs/batch_orchestrator_TIMESTAMP.log`**: Detailed log from Python script
- **`logs/orchestrator_console.log`**: Console output from background process

### Log Levels

- **INFO**: Normal operation (batch starts, completions, progress)
- **WARNING**: Non-critical issues (high memory, retries)
- **ERROR**: Problems that need attention (failed batches, missing files)

### Common Log Messages

**Normal operation:**
```
INFO - Starting batch 42
INFO - System Stats - Memory: 45.2% used, CPU: 78.5%
INFO - Batch 42 completed successfully
INFO - Cooldown: waiting 30s before next batch...
```

**High memory warning:**
```
WARNING - Memory usage high (87.3%), waiting for memory to free up...
```
Action: Reduce `batch_size` or increase `cooldown`

**Batch failure:**
```
ERROR - Batch 42 failed with error code 1
ERROR - Error output: [error details]
```
Action: Check the error details, may be model issue or corrupt image

**All files complete:**
```
INFO - All files processed! 🎉
INFO - BATCH ORCHESTRATOR SUMMARY
INFO - Files processed: 31,841 / 31,841 (100.0%)
```

## Troubleshooting

### Process Won't Start

**Symptom**: Error message "already running" when starting

**Solution**:
```bash
# Check if actually running
ps aux | grep batch_orchestrator

# If not running, remove stale PID file
rm batch_orchestrator.pid

# Try starting again
./scripts/run_batch_descriptions.sh
```

### Processing Stopped (Stale Status)

**Symptom**: `check_progress.py` shows "Processing appears to be stopped"

**Possible causes**:
1. Laptop went to sleep (caffeinate failed or disconnected from power)
2. Process crashed
3. Out of memory

**Solution**:
```bash
# Check if process is running
ps aux | grep batch_orchestrator

# If not running, check recent logs for errors
tail -50 logs/orchestrator_console.log

# Resume processing
./scripts/run_batch_descriptions.sh
```

### High Memory Usage

**Symptom**: Log shows memory warnings, processing is slow

**Solutions**:
1. **Reduce batch size**: Process fewer images per batch
   ```bash
   ./scripts/run_batch_descriptions.sh database/512x512 50 30
   ```

2. **Increase cooldown**: Give system more time to free memory
   ```bash
   ./scripts/run_batch_descriptions.sh database/512x512 100 60
   ```

3. **Close other applications**: Free up system memory

### Processing Too Slow

**Symptom**: Rate shows < 100 images/hour

**Solutions**:
1. **Increase batch size**: Process more images per batch (reduces overhead)
   ```bash
   ./scripts/run_batch_descriptions.sh database/512x512 200 30
   ```

2. **Decrease cooldown**: Less waiting between batches
   ```bash
   ./scripts/run_batch_descriptions.sh database/512x512 100 15
   ```

3. **Check system load**: Use `python src/progress_summary.py` to see if CPU/memory are maxed out

### Laptop Went to Sleep

**Symptom**: Processing stopped after closing lid

**Cause**: Power adapter disconnected, or caffeinate failed

**Solution**:
1. Always keep power adapter connected
2. Verify caffeinate is working:
   ```bash
   ps aux | grep caffeinate
   ```
3. Resume processing:
   ```bash
   ./scripts/run_batch_descriptions.sh
   ```

### Image Processing Errors

**Symptom**: Log shows individual image errors, but batches continue

**This is normal**: Some images may fail due to:
- Corrupt files
- Unsupported formats
- Missing files

**Action**: Check `progress_summary.py` for error rates:
- < 1% errors: Normal, no action needed
- \> 5% errors: Check logs for patterns, may need to fix images

### Can't Find Progress File

**Symptom**: Error about missing `photo_descriptions_progress.txt`

**This is normal** on first run. The file is created automatically as images are processed.

## System Requirements

### Hardware

- **Memory**: 16GB+ recommended (works with 8GB but use smaller batch sizes)
- **Disk Space**: ~150MB for logs and outputs (images must already be on disk)
- **CPU**: Any modern processor (M-series Macs are fast)
- **GPU**: Optional (SmolVLM can use GPU if available)

### Software

- **Python**: 3.12+
- **Pipenv**: For virtual environment
- **Dependencies**: Installed via `pipenv install`
- **macOS**: Tested on macOS (should work on Linux with minor modifications)

### Time Estimates

Based on typical M3 MacBook performance with SmolVLM:

- **Processing rate**: 300-400 images/hour
- **31,841 images**: ~80-105 hours (3-4 days)

**Recommendations**:
- Start on a Friday evening
- Let it run over the weekend
- Check progress Monday morning

### Batch Size Guidelines

| Available RAM | Recommended Batch Size | Cooldown |
|---------------|------------------------|----------|
| 8GB           | 50                     | 60s      |
| 16GB          | 100                    | 30s      |
| 32GB+         | 200                    | 15s      |

## Tips for Success

1. **Start with a test run**: Process 500 images first to verify everything works
   ```bash
   # Edit generate_descriptions.py to limit total files, or use a smaller directory
   ```

2. **Monitor the first hour**: Make sure memory stays reasonable and rate is good

3. **Use watch for monitoring**: Set up the auto-refresh dashboard and check occasionally

4. **Keep laptop plugged in**: Essential for lid-closed operation

5. **Check progress daily**: Quick check with `python src/check_progress.py`

6. **Don't worry about stopping**: It's completely safe to stop and resume

7. **Log files grow**: You can delete old logs from `logs/` to save space

## Advanced Usage

### Custom Model Parameters

Edit `src/generate_descriptions.py` to modify:
- Prompt text
- Temperature
- Max tokens
- Other model parameters

### Processing Different Directories

The system works with any directory of images:

```bash
./scripts/run_batch_descriptions.sh /path/to/other/images 100 30
```

### Multiple Simultaneous Runs

You can run multiple orchestrators on different directories:
1. Each needs its own directory with different progress files
2. Use different PID file names
3. Monitor system resources to avoid overload

### SSH Monitoring

You can SSH into your Mac from another device to check progress:

```bash
ssh user@your-mac.local
cd /path/to/photomanage
python src/check_progress.py
```

## Support

If you encounter issues not covered here:

1. Check the detailed logs in `logs/` directory
2. Review the progress summary: `python src/progress_summary.py`
3. Look for patterns in errors
4. Consider adjusting batch size and cooldown parameters

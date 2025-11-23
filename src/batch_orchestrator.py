#!/usr/bin/env python3
"""
Batch Orchestrator for Image Description Generation

This script orchestrates the processing of large numbers of images by:
1. Running generate_descriptions.py in batches
2. Spawning a fresh Python process for each batch (prevents memory leaks)
3. Adding cooldown periods between batches
4. Monitoring system resources
5. Providing comprehensive logging

Usage:
    python src/batch_orchestrator.py <directory> [options]

Example:
    python src/batch_orchestrator.py database/512x512 --batch-size 100 --cooldown 30
"""

import argparse
import logging
import os
import psutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class BatchOrchestrator:
    """Orchestrates batch processing of images with memory management."""

    def __init__(self, directory: str, batch_size: int = 100,
                 cooldown: int = 30, model: str = 'smolvlm',
                 max_memory_percent: float = 85.0,
                 max_tokens: int = 500, temp: float = 0.0):
        self.directory = Path(directory)
        self.batch_size = batch_size
        self.cooldown = cooldown
        self.model = model
        self.max_memory_percent = max_memory_percent
        self.max_tokens = max_tokens
        self.temp = temp
        self.progress_file = "photo_descriptions_progress.txt"

        # Set up logging
        self.setup_logging()

        # Get total file count
        self.total_files = self._count_files()
        self.logger.info(f"Total files in directory: {self.total_files}")

    def setup_logging(self):
        """Set up logging to both file and console."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"batch_orchestrator_{timestamp}.log"

        # Create logger
        self.logger = logging.getLogger("BatchOrchestrator")
        self.logger.setLevel(logging.INFO)

        # File handler - detailed
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler - concise
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Logging to: {log_file}")

    def _count_files(self) -> int:
        """Count total files in directory."""
        count = 0
        skip_files = {'.ds_store', 'thumbs.db', '.gitignore', '.gitkeep'}

        for path in self.directory.rglob('*'):
            if path.is_file():
                if not path.name.startswith('.') and path.name.lower() not in skip_files:
                    count += 1
        return count

    def get_completed_count(self) -> int:
        """Get count of already completed files."""
        if not os.path.exists(self.progress_file):
            return 0

        with open(self.progress_file, 'r') as f:
            return sum(1 for line in f if line.strip())

    def check_memory(self) -> tuple[bool, float]:
        """
        Check if system memory is within acceptable limits.

        Returns:
            Tuple of (is_ok, current_percent)
        """
        memory = psutil.virtual_memory()
        percent_used = memory.percent

        is_ok = percent_used < self.max_memory_percent
        return is_ok, percent_used

    def log_system_stats(self):
        """Log current system statistics."""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)

        self.logger.info(
            f"System Stats - Memory: {memory.percent:.1f}% used "
            f"({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB), "
            f"CPU: {cpu_percent:.1f}%"
        )

    def run_batch(self, batch_num: int) -> bool:
        """
        Run a single batch of image descriptions.

        Args:
            batch_num: The batch number (for logging)

        Returns:
            True if batch completed successfully, False otherwise
        """
        self.logger.info(f"Starting batch {batch_num}")
        self.log_system_stats()

        # Check memory before starting
        memory_ok, memory_percent = self.check_memory()
        if not memory_ok:
            self.logger.warning(
                f"Memory usage high ({memory_percent:.1f}%), "
                f"waiting for memory to free up..."
            )
            time.sleep(60)
            memory_ok, memory_percent = self.check_memory()
            if not memory_ok:
                self.logger.error(
                    f"Memory still high ({memory_percent:.1f}%), skipping batch"
                )
                return False

        # Build command
        cmd = [
            sys.executable,
            "src/generate_descriptions.py",
            str(self.directory),
            str(self.batch_size),
            "--model", self.model,
            "--max-tokens", str(self.max_tokens),
            "--temp", str(self.temp)
        ]

        self.logger.info(f"Running: {' '.join(cmd)}")

        try:
            # Run as subprocess - this is KEY for memory management
            # When the process exits, ALL memory is freed
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            self.logger.info(f"Batch {batch_num} completed successfully")
            self.logger.debug(f"Output: {result.stdout}")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Batch {batch_num} failed with error code {e.returncode}")
            self.logger.error(f"Error output: {e.stderr}")
            return False

        except Exception as e:
            self.logger.error(f"Unexpected error in batch {batch_num}: {e}")
            return False

    def run(self):
        """Main orchestration loop."""
        self.logger.info("=" * 70)
        self.logger.info("BATCH ORCHESTRATOR STARTED")
        self.logger.info(f"Directory: {self.directory}")
        self.logger.info(f"Total files: {self.total_files}")
        self.logger.info(f"Batch size: {self.batch_size}")
        self.logger.info(f"Cooldown: {self.cooldown}s")
        self.logger.info(f"Model: {self.model}")
        self.logger.info(f"Max tokens: {self.max_tokens}")
        self.logger.info(f"Temperature: {self.temp}")
        self.logger.info("=" * 70)

        batch_num = 0
        successful_batches = 0
        failed_batches = 0
        start_time = time.time()

        try:
            while True:
                batch_num += 1

                # Check how many files are left
                completed = self.get_completed_count()
                remaining = self.total_files - completed

                if remaining <= 0:
                    self.logger.info("All files processed! 🎉")
                    break

                percent_complete = (completed / self.total_files) * 100
                self.logger.info(
                    f"Progress: {completed:,} / {self.total_files:,} "
                    f"({percent_complete:.1f}%) - {remaining:,} remaining"
                )

                # Run the batch
                success = self.run_batch(batch_num)

                if success:
                    successful_batches += 1
                else:
                    failed_batches += 1
                    self.logger.warning(f"Failed batches so far: {failed_batches}")

                # Check if we're done
                completed_after = self.get_completed_count()
                if completed_after >= self.total_files:
                    self.logger.info("All files processed! 🎉")
                    break

                # Cooldown period
                self.logger.info(f"Cooldown: waiting {self.cooldown}s before next batch...")
                time.sleep(self.cooldown)

        except KeyboardInterrupt:
            self.logger.info("\nReceived interrupt signal - stopping gracefully")

        except Exception as e:
            self.logger.error(f"Unexpected error in orchestrator: {e}", exc_info=True)

        finally:
            # Final summary
            elapsed_time = time.time() - start_time
            elapsed_hours = elapsed_time / 3600

            final_completed = self.get_completed_count()
            final_percent = (final_completed / self.total_files) * 100

            self.logger.info("=" * 70)
            self.logger.info("BATCH ORCHESTRATOR SUMMARY")
            self.logger.info(f"Total batches run: {batch_num}")
            self.logger.info(f"Successful: {successful_batches}")
            self.logger.info(f"Failed: {failed_batches}")
            self.logger.info(f"Files processed: {final_completed:,} / {self.total_files:,} ({final_percent:.1f}%)")
            self.logger.info(f"Elapsed time: {elapsed_hours:.2f} hours")
            if final_completed > 0:
                rate = final_completed / elapsed_hours
                self.logger.info(f"Average rate: {rate:.0f} images/hour")
            self.logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Batch orchestrator for image description generation"
    )
    parser.add_argument(
        'directory',
        help='Directory containing images to process'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of images to process per batch (default: 100)'
    )
    parser.add_argument(
        '--cooldown',
        type=int,
        default=30,
        help='Seconds to wait between batches (default: 30)'
    )
    parser.add_argument(
        '--model',
        choices=['smolvlm', 'smolvlm2'],
        default='smolvlm',
        help='Model to use for descriptions (default: smolvlm)'
    )
    parser.add_argument(
        '--max-memory',
        type=float,
        default=85.0,
        help='Maximum memory usage percent before pausing (default: 85.0)'
    )
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=500,
        help='Maximum tokens to generate per image (default: 500)'
    )
    parser.add_argument(
        '--temp',
        type=float,
        default=0.0,
        help='Temperature for generation (default: 0.0)'
    )

    args = parser.parse_args()

    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: Directory not found: {args.directory}")
        sys.exit(1)

    # Create and run orchestrator
    orchestrator = BatchOrchestrator(
        directory=args.directory,
        batch_size=args.batch_size,
        cooldown=args.cooldown,
        model=args.model,
        max_memory_percent=args.max_memory,
        max_tokens=args.max_tokens,
        temp=args.temp
    )

    orchestrator.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
# ]
# ///

"""
Generate photo descriptions using SmolVLM or SmolVLM2 models.

This script uses the SmolVLMHelper or SmolVLM2Helper classes to generate
descriptions for images in a directory. It supports progress tracking to
allow resuming from where you left off.

Usage:
    python src/generate_descriptions.py <directory> <num_files> [--model smolvlm|smolvlm2]

Example:
    python src/generate_descriptions.py ~/Photos 100 --model smolvlm2
"""

import click
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Set, List

# Progress tracking
PROGRESS_FILE = "photo_descriptions_progress.txt"


def load_progress_file() -> Set[str]:
    """Load the set of already processed files from the progress file."""
    if not os.path.exists(PROGRESS_FILE):
        return set()

    with open(PROGRESS_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())


def append_to_progress_file(file_path: str):
    """Append a processed file path to the progress file."""
    with open(PROGRESS_FILE, 'a') as f:
        f.write(f"{file_path}\n")


def delete_progress_file():
    """Delete the progress file to start fresh."""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)


def find_all_files(directory: str) -> tuple[List[Path], Path]:
    """
    Recursively find all files in a directory.
    No extension filtering - processes all files.
    Skips hidden files and common non-image files.

    Returns:
        Tuple of (list of file paths, base directory path)
    """
    files = []
    directory_path = Path(directory).resolve()

    # Files to skip
    skip_files = {'.ds_store', 'thumbs.db', '.gitignore', '.gitkeep'}

    for path in directory_path.rglob('*'):
        if path.is_file():
            # Skip hidden files and known non-image files
            if not path.name.startswith('.') and path.name.lower() not in skip_files:
                files.append(path)

    # Sort files alphabetically for predictable processing order
    files.sort()

    return files, directory_path


def prompt_resume() -> bool:
    """Ask user if they want to resume from previous progress."""
    response = input("Progress file found. Resume from previous run? (y/n): ").strip().lower()
    return response in ('y', 'yes')


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('num_files', type=int)
@click.option('--model', type=click.Choice(['smolvlm', 'smolvlm2'], case_sensitive=False),
              default='smolvlm', help='Model to use (default: smolvlm)')
@click.option('--output-dir', default='outputs', help='Directory for output files')
@click.option('--prompt', default='<image>Describe this image in detail',
              help='Prompt to use for image description (will auto-add <image> token if missing)')
@click.option('--max-tokens', default=500, type=int, help='Maximum tokens to generate (default: 500)')
@click.option('--temp', default=0.0, type=float, help='Temperature for generation, range 0.0-1.0 (default: 0.0)')
def main(directory, num_files, model, output_dir, prompt, max_tokens, temp):
    """
    Generate descriptions for images in a directory using SmolVLM models.

    DIRECTORY: Path to directory containing images
    NUM_FILES: Number of images to process in this run
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    output_file = os.path.join(output_dir, "image_analysis.json")

    # Check for existing progress file and output file
    completed_files = set()
    if os.path.exists(PROGRESS_FILE):
        # Check if output file also exists (consistent state)
        if not os.path.exists(output_file):
            click.echo("Warning: Progress file exists but output file is missing.")
            click.echo("This indicates an inconsistent state. Starting fresh.")
            delete_progress_file()
            click.echo("Deleted progress file. Starting fresh.")
        elif prompt_resume():
            completed_files = load_progress_file()
            click.echo(f"Resuming: {len(completed_files)} files already processed")
        else:
            delete_progress_file()
            click.echo("Starting fresh")

    # Find all files in directory
    click.echo(f"Scanning directory: {directory}")
    all_files, base_path = find_all_files(directory)

    if not all_files:
        click.echo("No files found in the specified directory.")
        return

    click.echo(f"Found {len(all_files)} total files")

    # Filter out already completed files
    files_to_process = [
        f for f in all_files
        if str(f.relative_to(base_path)) not in completed_files
    ]

    if not files_to_process:
        click.echo("All files have already been processed!")
        return

    click.echo(f"Files remaining to process: {len(files_to_process)}")

    # Limit to the specified number of files
    files_to_process = files_to_process[:num_files]
    click.echo(f"Processing {len(files_to_process)} files in this run")

    # Load the appropriate model
    click.echo(f"\nLoading {model} model...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if model.lower() == 'smolvlm2':
        # Import here to avoid loading both models
        from smolvlm2_helper import SmolVLM2Helper
        vlm = SmolVLM2Helper()
    else:
        from smolvlm_helper import SmolVLMHelper
        vlm = SmolVLMHelper()

    # Ensure prompt has <image> token
    if '<image>' not in prompt:
        prompt = f"<image>{prompt}"
        click.echo(f"Note: Added <image> token to prompt")

    # Process images and collect results
    results = []
    click.echo(f"\nProcessing images with prompt: '{prompt}'")
    click.echo(f"Temperature: {temp}, Max tokens: {max_tokens}\n")

    for i, image_path in enumerate(files_to_process, 1):
        # Get relative path from input directory
        rel_path = image_path.relative_to(base_path)

        click.echo(f"[{i}/{len(files_to_process)}] Processing: {rel_path}")

        try:
            # Time the description generation
            start_time = time.time()

            description = vlm.describe_image(
                str(image_path),
                prompt=prompt,
                temp=temp,
                max_tokens=max_tokens,
                verbose=False
            )

            elapsed_time = time.time() - start_time

            # Extract text from GenerationResult if needed
            if hasattr(description, 'text'):
                description_text = description.text
            else:
                description_text = str(description)

            results.append({
                "file": f"./{rel_path}",
                "description": description_text.strip(),
                "model": model,
                "generation_time_seconds": round(elapsed_time, 2),
                "error": False
            })

            click.echo(f"  Completed in {elapsed_time:.2f}s")

            # Save to progress file after successful processing
            append_to_progress_file(str(rel_path))

        except Exception as e:
            click.echo(f"  Error processing {rel_path}: {e}", err=True)
            results.append({
                "file": f"./{rel_path}",
                "description": f"Error: {str(e)}",
                "model": model,
                "generation_time_seconds": None,
                "error": True
            })

            # Track failed files to prevent duplicate entries on resume
            append_to_progress_file(str(rel_path))

    # Load existing results if file exists
    all_results = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
            click.echo(f"Loaded {len(all_results)} existing results from {output_file}")
        except (json.JSONDecodeError, IOError) as e:
            click.echo(f"Error: Could not read existing results file: {e}", err=True)
            click.echo(f"The file may be corrupted or inaccessible: {output_file}", err=True)

            # Auto-exit in non-interactive mode (e.g., batch processing)
            if not sys.stdin.isatty():
                click.echo("Running in non-interactive mode. Exiting to prevent data loss.", err=True)
                sys.exit(1)

            # In interactive mode, prompt user
            response = input("Continue anyway? This may overwrite existing data. (y/n): ").strip().lower()
            if response not in ('y', 'yes'):
                click.echo("Exiting to prevent data loss. Please fix the JSON file and try again.")
                sys.exit(1)
            click.echo("Continuing with empty results. Previous data will be lost.")
            all_results = []

    # Append new results
    all_results.extend(results)

    # Write all results to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Count successes and errors for this batch
    successful = sum(1 for r in results if not r.get('error', False))
    failed = sum(1 for r in results if r.get('error', False))

    # Count cumulative totals
    total_successful = sum(1 for r in all_results if not r.get('error', False))
    total_failed = sum(1 for r in all_results if r.get('error', False))

    click.echo(f"\n✓ Analysis complete!")
    click.echo(f"  This batch: {len(results)} files ({successful} successful, {failed} failed)")
    click.echo(f"  Cumulative total: {len(all_results)} files ({total_successful} successful, {total_failed} failed)")
    click.echo(f"  Output saved to: {output_file}")
    click.echo(f"  Progress tracked in: {PROGRESS_FILE}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Compute Laplacian sharpness scores for truncated description thumbnails.

Reads outputs/v2/truncated_descriptions.yaml, loads each corresponding
512x512 thumbnail, and computes the variance of the Laplacian as a
sharpness score. Higher = sharper; lower = blurry or featureless.

Usage:
    python scripts/laplacian_sharpness.py
    python scripts/laplacian_sharpness.py --input outputs/v2/truncated_descriptions.yaml
    python scripts/laplacian_sharpness.py --thumb-dir database/512x512 --output outputs/v2/sharpness_scores.json
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import yaml


DEFAULT_INPUT = "outputs/v2/truncated_descriptions.yaml"
DEFAULT_THUMB_DIR = "database/512x512"
DEFAULT_OUTPUT = "outputs/v2/sharpness_scores.json"


def laplacian_variance(image_path: Path) -> float | None:
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    return float(cv2.Laplacian(img, cv2.CV_64F).var())


def main():
    parser = argparse.ArgumentParser(description="Laplacian sharpness scoring for truncated descriptions")
    parser.add_argument("--input", default=DEFAULT_INPUT, help=f"Truncated descriptions YAML (default: {DEFAULT_INPUT})")
    parser.add_argument("--thumb-dir", default=DEFAULT_THUMB_DIR, help=f"Thumbnail root directory (default: {DEFAULT_THUMB_DIR})")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Output JSON file (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    thumb_dir = Path(args.thumb_dir)

    with open(args.input) as f:
        entries = yaml.safe_load(f)

    print(f"Scoring {len(entries):,} images...")

    results = []
    missing = 0

    for entry in entries:
        # ./0/filename.ext -> database/512x512/0/filename.ext
        rel = Path(entry["file"])
        thumb_path = thumb_dir / rel.parts[-2] / rel.name

        score = laplacian_variance(thumb_path)
        if score is None:
            missing += 1

        results.append({
            "file": entry["file"],
            "sharpness": score,
        })

    results.sort(key=lambda x: (x["sharpness"] is None, x["sharpness"] or 0))

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    scored = len(results) - missing
    scores = [r["sharpness"] for r in results if r["sharpness"] is not None]
    print(f"Scored:  {scored:,} / {len(results):,}")
    if missing:
        print(f"Missing: {missing:,} thumbnails not found")
    print(f"Min:     {min(scores):.1f}")
    print(f"Median:  {float(np.median(scores)):.1f}")
    print(f"Max:     {max(scores):.1f}")
    print(f"Written: {args.output}")


if __name__ == "__main__":
    main()

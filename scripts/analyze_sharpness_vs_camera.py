#!/usr/bin/env python3
"""
Analyze Laplacian sharpness scores against camera EXIF settings.

Joins image_sharpness and exif_camera tables to show how sharpness
correlates with ISO, aperture, and shutter speed. Run against the
truncated set by default (image_sharpness contains only truncated images).

Usage:
    python scripts/analyze_sharpness_vs_camera.py
    python scripts/analyze_sharpness_vs_camera.py --db database/mediameta.db
"""

import argparse
import sqlite3
from fractions import Fraction

import numpy as np


DEFAULT_DB = "database/mediameta.db"


def parse_exposure(val) -> float | None:
    try:
        return float(Fraction(str(val)))
    except Exception:
        return None


def parse_iso(val) -> int | None:
    try:
        return int(str(val).split(",")[0].strip())
    except Exception:
        return None


def parse_fnumber(val) -> float | None:
    try:
        return float(val)
    except Exception:
        return None


def print_table(title, buckets, data, key_fn):
    print(f"\n--- {title} ---")
    print(f"  {'Bucket':<30} {'n':>6}  {'Median':>8}  {'Mean':>8}")
    print(f"  {'-'*30} {'------':>6}  {'------':>8}  {'------':>8}")
    for label, fn in buckets:
        scores = [d[0] for d in data if key_fn(d) is not None and fn(key_fn(d))]
        if scores:
            print(f"  {label:<30} {len(scores):>6,}  {np.median(scores):>8.1f}  {np.mean(scores):>8.1f}")


def main():
    parser = argparse.ArgumentParser(description="Analyze sharpness vs camera settings")
    parser.add_argument("--db", default=DEFAULT_DB, help=f"SQLite database (default: {DEFAULT_DB})")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)

    rows = conn.execute("""
        SELECT s.sharpness, c.ExposureTime, c.FNumber, c.ISO
        FROM image_sharpness s
        JOIN exif_camera c ON s.SourceFile = c.SourceFile
        WHERE s.sharpness IS NOT NULL
    """).fetchall()

    print(f"Rows with sharpness + camera data: {len(rows):,}")

    # Parse into typed tuples: (sharpness, exposure_secs, fnumber, iso)
    data = []
    for sharpness, exposure, fnumber, iso in rows:
        data.append((
            sharpness,
            parse_exposure(exposure),
            parse_fnumber(fnumber),
            parse_iso(iso),
        ))

    shutter_buckets = [
        ("< 1/500s (fast)",     lambda t: t < 1/500),
        ("1/500 – 1/100s",      lambda t: 1/500 <= t < 1/100),
        ("1/100 – 1/30s",       lambda t: 1/100 <= t < 1/30),
        ("> 1/30s (slow)",      lambda t: t >= 1/30),
    ]
    print_table("Shutter Speed vs Sharpness", shutter_buckets, data, lambda d: d[1])

    aperture_buckets = [
        ("f/1 – f/2   (very wide)",  lambda f: f <= 2.0),
        ("f/2 – f/4   (wide)",       lambda f: 2.0 < f <= 4.0),
        ("f/4 – f/8   (mid)",        lambda f: 4.0 < f <= 8.0),
        ("f/8+        (narrow)",     lambda f: f > 8.0),
    ]
    print_table("Aperture vs Sharpness", aperture_buckets, data, lambda d: d[2])

    iso_buckets = [
        ("ISO <= 100",    lambda i: i <= 100),
        ("ISO 101–400",   lambda i: 100 < i <= 400),
        ("ISO 401–1600",  lambda i: 400 < i <= 1600),
        ("ISO > 1600",    lambda i: i > 1600),
    ]
    print_table("ISO vs Sharpness", iso_buckets, data, lambda d: d[3])

    print()


if __name__ == "__main__":
    main()

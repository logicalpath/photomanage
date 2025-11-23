#!/usr/bin/env python3
"""
Update the prefixed_path column in the exif table based on datasette/media_config.yaml

This script reads the media prefix path from the configuration file and updates
all rows in the exif table to regenerate the prefixed_path column.

Usage:
    python src/update_prefix_path.py
"""

import sqlite3
import yaml
import os
import sys


def load_config(config_path="datasette/media_config.yaml"):
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        print(f"Error: Configuration file '{config_path}' not found")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def update_prefixed_paths(db_path, media_prefix_path):
    """Update the prefixed_path column in the exif table"""

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count rows before update
    cursor.execute("SELECT COUNT(*) FROM exif")
    total_rows = cursor.fetchone()[0]
    print(f"Found {total_rows} rows in exif table")

    # Update prefixed_path by concatenating prefix with path (removing leading '.')
    # substr(SourceFile, 2) removes the first character (the '.')
    update_sql = """
    UPDATE exif
    SET prefixed_path = ? || substr(SourceFile, 2)
    """

    print(f"Updating prefixed_path with prefix: {media_prefix_path}")
    cursor.execute(update_sql, (media_prefix_path,))

    # Commit changes
    conn.commit()
    rows_updated = cursor.rowcount
    print(f"Successfully updated {rows_updated} rows")

    # Show sample results
    cursor.execute("SELECT SourceFile, prefixed_path FROM exif LIMIT 3")
    print("\nSample results:")
    for row in cursor.fetchall():
        print(f"  SourceFile: {row[0]}")
        print(f"  prefixed_path: {row[1]}\n")

    conn.close()


def main():
    # Load configuration
    config = load_config()

    media_prefix_path = config.get('media_prefix_path')
    database_path = config.get('database_path')

    if not media_prefix_path:
        print("Error: 'media_prefix_path' not found in configuration")
        sys.exit(1)

    if not database_path:
        print("Error: 'database_path' not found in configuration")
        sys.exit(1)

    if not os.path.exists(database_path):
        print(f"Error: Database file '{database_path}' not found")
        sys.exit(1)

    print(f"Configuration loaded:")
    print(f"  Media prefix path: {media_prefix_path}")
    print(f"  Database path: {database_path}\n")

    # Update the prefixed paths
    update_prefixed_paths(database_path, media_prefix_path)

    print("\n✓ Update complete!")


if __name__ == "__main__":
    main()

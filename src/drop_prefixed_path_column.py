#!/usr/bin/env python3
"""
Drop the prefixed_path column from exif table

This script removes the now-redundant prefixed_path column from the exif table.
The full_path is now computed dynamically via the exif_with_fullpath view.

Safety: This is a destructive operation. Make sure you have a database backup
and that the exif_with_fullpath view is working correctly before running.

Usage:
    python src/drop_prefixed_path_column.py
"""

import sqlite3
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "mediameta.db"


def verify_view_exists(cursor):
    """Verify that exif_with_fullpath view exists"""
    print("Verifying exif_with_fullpath view exists...")

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='view' AND name='exif_with_fullpath'"
    )

    if not cursor.fetchone():
        print("  ✗ Error: exif_with_fullpath view does not exist!")
        print("  Run migrate_to_config_table.py first")
        return False

    print("  ✓ View exists")
    return True


def verify_config_exists(cursor):
    """Verify that photomanage_config table has media_prefix_path"""
    print("Verifying photomanage_config has media_prefix_path...")

    cursor.execute(
        "SELECT value FROM photomanage_config WHERE key='media_prefix_path'"
    )

    result = cursor.fetchone()
    if not result:
        print("  ✗ Error: media_prefix_path not found in photomanage_config!")
        return False

    print(f"  ✓ Found prefix: {result[0]}")
    return True


def drop_column(cursor):
    """Drop the prefixed_path column from exif table"""
    print("\nDropping prefixed_path column from exif table...")

    # Get the current table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='exif'")
    schema = cursor.fetchone()[0]

    print("  Current schema:")
    print(f"  {schema}")

    # Check if prefixed_path exists
    if 'prefixed_path' not in schema.lower():
        print("  ! Column prefixed_path does not exist - nothing to drop")
        return True

    # SQLite 3.35.0+ supports ALTER TABLE DROP COLUMN
    # prefixed_path meets requirements: not a PK, no UNIQUE, not indexed, not in constraints
    print("\n  Executing ALTER TABLE DROP COLUMN...")
    cursor.execute("ALTER TABLE exif DROP COLUMN prefixed_path")
    print("  ✓ Column dropped successfully")

    return True


def verify_view_still_works(cursor):
    """Verify that exif_with_fullpath view still works after column drop"""
    print("\nVerifying exif_with_fullpath view still works...")

    cursor.execute("SELECT SourceFile, full_path FROM exif_with_fullpath LIMIT 3")
    rows = cursor.fetchall()

    if not rows:
        print("  ✗ Error: View returned no results!")
        return False

    for source, full in rows:
        print(f"  {source} -> {full}")

    print("  ✓ View works correctly")
    return True


def main():
    """Main function"""
    print("=" * 60)
    print("Drop prefixed_path column from exif table")
    print("=" * 60)
    print("\nWARNING: This is a destructive operation!")
    print("Make sure you have a database backup before proceeding.")
    print()

    response = input("Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Aborted.")
        sys.exit(0)

    # Check database exists
    if not DATABASE_PATH.exists():
        print(f"\n✗ Error: Database not found at {DATABASE_PATH}")
        sys.exit(1)

    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Verify prerequisites
        if not verify_view_exists(cursor):
            sys.exit(1)

        if not verify_config_exists(cursor):
            sys.exit(1)

        # Drop the column
        if not drop_column(cursor):
            print("\n✗ Failed to drop column")
            conn.rollback()
            sys.exit(1)

        # Verify view still works
        if not verify_view_still_works(cursor):
            print("\n✗ View verification failed - rolling back")
            conn.rollback()
            sys.exit(1)

        # Commit changes
        conn.commit()

        print("\n" + "=" * 60)
        print("✓ Successfully dropped prefixed_path column!")
        print("=" * 60)
        print("\nThe exif table now only contains source columns.")
        print("Full paths are computed via exif_with_fullpath view.")
        print()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()

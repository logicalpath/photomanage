#!/usr/bin/env python3
"""
Migrate to photomanage_config table and exif_with_fullpath view

This script migrates from the YAML + prefixed_path column approach to a
database-native configuration approach using a config table and view.

What it does:
1. Creates photomanage_config table
2. Reads current prefix from media_config.yaml
3. Inserts configuration into database
4. Creates exif_with_fullpath view for dynamic path computation
5. Verifies paths match existing prefixed_path column

Safety features:
- Idempotent (can run multiple times)
- Transaction-based (rollback on error)
- Validates before making changes
- Keeps existing prefixed_path column for rollback

Usage:
    python src/migrate_to_config_table.py
"""

import sqlite3
import sys
import yaml
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "mediameta.db"
CONFIG_PATH = PROJECT_ROOT / "media_config.yaml"


def read_media_config():
    """Read the media prefix path from media_config.yaml"""
    print("Reading media prefix from media_config.yaml...")

    if not CONFIG_PATH.exists():
        print(f"  ✗ Error: {CONFIG_PATH} not found")
        sys.exit(1)

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)

        media_prefix = config.get('media_prefix_path')
        if not media_prefix:
            print("  ✗ Error: media_prefix_path not found in config")
            sys.exit(1)

        print(f"  ✓ Found: {media_prefix}")
        return media_prefix

    except Exception as e:
        print(f"  ✗ Error reading config: {e}")
        sys.exit(1)


def create_config_table(cursor):
    """Create the photomanage_config table"""
    print("\nCreating photomanage_config table...")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photomanage_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Table created")


def insert_configuration(cursor, media_prefix):
    """Insert the media prefix configuration"""
    print("\nInserting configuration...")

    # Check if configuration already exists
    cursor.execute(
        "SELECT value FROM photomanage_config WHERE key = 'media_prefix_path'"
    )
    existing = cursor.fetchone()

    if existing:
        existing_value = existing[0]
        if existing_value == media_prefix:
            print(f"  ✓ Configuration already exists with same value: {media_prefix}")
        else:
            print(f"  ! Configuration exists with different value:")
            print(f"    Existing: {existing_value}")
            print(f"    New:      {media_prefix}")
            print(f"  Updating to new value...")
            cursor.execute(
                """UPDATE photomanage_config
                   SET value = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE key = 'media_prefix_path'""",
                (media_prefix,)
            )
            print("  ✓ Updated media_prefix_path")
    else:
        cursor.execute(
            """INSERT INTO photomanage_config (key, value, description)
               VALUES (?, ?, ?)""",
            ('media_prefix_path',
             media_prefix,
             'Absolute path prefix for media files')
        )
        print("  ✓ Inserted media_prefix_path")


def create_view(cursor):
    """Create the exif_with_fullpath view"""
    print("\nCreating exif_with_fullpath view...")

    # Drop view if it exists (to handle updates)
    cursor.execute("DROP VIEW IF EXISTS exif_with_fullpath")

    cursor.execute("""
        CREATE VIEW exif_with_fullpath AS
        SELECT
            exif.*,
            (SELECT value FROM photomanage_config WHERE key = 'media_prefix_path')
            || substr(SourceFile, 2) as full_path
        FROM exif
    """)
    print("  ✓ View created")


def verify_migration(cursor):
    """Verify that computed paths match existing prefixed_path"""
    print("\nVerifying migration...")

    # Get a sample of rows to compare
    cursor.execute("""
        SELECT
            SourceFile,
            prefixed_path,
            full_path,
            CASE
                WHEN prefixed_path = full_path THEN 1
                ELSE 0
            END as matches
        FROM exif_with_fullpath
        WHERE prefixed_path IS NOT NULL
        LIMIT 10
    """)

    rows = cursor.fetchall()

    if not rows:
        print("  ! Warning: No rows with prefixed_path found to verify")
        return True

    all_match = True
    for i, (source_file, old_path, new_path, matches) in enumerate(rows):
        if i == 0:  # Show first example
            print(f"  Sample comparison:")
            print(f"    SourceFile:     {source_file}")
            print(f"    prefixed_path:  {old_path}")
            print(f"    full_path:      {new_path}")

        if not matches:
            print(f"  ✗ MISMATCH: {source_file}")
            print(f"    Expected: {old_path}")
            print(f"    Got:      {new_path}")
            all_match = False

    if all_match:
        print("  ✓ All sampled paths match!")

        # Count total matches
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN prefixed_path = full_path THEN 1 ELSE 0 END) as matches
            FROM exif_with_fullpath
            WHERE prefixed_path IS NOT NULL
        """)
        total, matches = cursor.fetchone()
        print(f"  ✓ Verified {matches}/{total} rows match")

        if matches != total:
            print(f"  ! Warning: {total - matches} rows don't match")
            return False

    return all_match


def main():
    """Main migration function"""
    print("=" * 60)
    print("Migration: photomanage_config table + exif_with_fullpath view")
    print("=" * 60)

    # Check database exists
    if not DATABASE_PATH.exists():
        print(f"\n✗ Error: Database not found at {DATABASE_PATH}")
        sys.exit(1)

    # Read configuration
    media_prefix = read_media_config()

    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Perform migration steps
        create_config_table(cursor)
        insert_configuration(cursor, media_prefix)
        create_view(cursor)

        # Verify before committing
        if not verify_migration(cursor):
            print("\n✗ Verification failed - rolling back")
            conn.rollback()
            sys.exit(1)

        # Commit changes
        conn.commit()

        print("\n" + "=" * 60)
        print("✓ Migration complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update datasette.yaml to use exif_with_fullpath view")
        print("2. Test Datasette functionality")
        print("3. After validation, consider dropping prefixed_path column")
        print()

    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()

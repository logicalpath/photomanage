#!/usr/bin/env python3
"""
Create database indexes for photomanage

This script creates indexes on frequently queried columns to improve
query performance. Run this once to optimize the database.

Usage:
    python src/create_indexes.py
"""

import re
import sqlite3
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "mediameta.db"


def validate_sql_identifier(identifier, identifier_type="identifier"):
    """
    Validate SQL identifier to prevent SQL injection.

    SQLite identifiers must start with a letter or underscore,
    followed by letters, numbers, or underscores.
    """
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid {identifier_type}: {identifier}")
    return identifier


def create_indexes(db_path):
    """Create indexes on frequently queried columns"""

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    indexes = [
        # CRITICAL: FileName lookup for media plugin
        ("idx_exif_filename", "exif", "FileName"),

        # CRITICAL: thumbImages path for JOINs (FK target)
        ("idx_thumbimages_path", "thumbImages", "path"),

        # HIGH: CreateDate for date-based queries and sorting
        ("idx_exif_createdate", "exif", "CreateDate"),

        # MEDIUM: AI description file for JOINs
        ("idx_ai_description_file", "ai_description", "file"),
    ]

    print(f"Creating indexes on {db_path.name}...")
    print()

    for index_name, table, column in indexes:
        try:
            # Validate identifiers to prevent SQL injection
            validate_sql_identifier(index_name, "index name")
            validate_sql_identifier(table, "table name")
            validate_sql_identifier(column, "column name")

            # Check if index already exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                (index_name,)
            )
            if cursor.fetchone():
                print(f"✓ Index {index_name} already exists")
                continue

            # Create the index
            sql = f"CREATE INDEX {index_name} ON {table}({column})"
            cursor.execute(sql)
            print(f"✓ Created index: {index_name} on {table}({column})")

        except sqlite3.Error as e:
            print(f"✗ Error creating {index_name}: {e}")
            conn.rollback()
            continue

    # Commit all changes
    conn.commit()

    # Show index statistics
    print()
    print("Index summary:")
    cursor.execute("""
        SELECT name, tbl_name
        FROM sqlite_master
        WHERE type='index' AND sql IS NOT NULL
        ORDER BY tbl_name, name
    """)

    for row in cursor.fetchall():
        print(f"  {row[1]}: {row[0]}")

    conn.close()
    print()
    print("Index creation complete!")

if __name__ == "__main__":
    create_indexes(DATABASE_PATH)

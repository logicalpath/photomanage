#!/usr/bin/env python3
"""
Load 512x512 thumbnails into the thumbImages table.
Transforms paths from database/512x512/0/file.jpg to ./0/file.jpg
"""

import sqlite3
from pathlib import Path
import sys

def load_thumbnails():
    db_path = 'database/mediameta.db'
    thumbs_dir = Path('database/512x512')

    if not thumbs_dir.exists():
        print(f"Error: {thumbs_dir} does not exist")
        sys.exit(1)

    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing thumbnails
    print("Clearing existing thumbnails...")
    cursor.execute('DELETE FROM thumbImages')
    deleted_count = cursor.rowcount
    print(f"Deleted {deleted_count} old thumbnails")
    conn.commit()

    # Insert new thumbnails
    print(f"\nLoading thumbnails from {thumbs_dir}...")
    count = 0
    errors = 0

    for file_path in sorted(thumbs_dir.rglob('*')):
        if file_path.is_file():
            try:
                # Read file content
                with open(file_path, 'rb') as f:
                    content = f.read()

                # Transform path: database/512x512/0/file.jpg -> ./0/file.jpg
                relative = file_path.relative_to(thumbs_dir)
                db_path_str = f'./{relative}'

                # Get file size
                size = file_path.stat().st_size

                # Insert
                cursor.execute(
                    'INSERT INTO thumbImages (path, content, size, should_be_deleted) VALUES (?, ?, ?, 0)',
                    (db_path_str, content, size)
                )
                count += 1

                if count % 1000 == 0:
                    print(f'  Processed {count} files...')
                    conn.commit()

            except Exception as e:
                errors += 1
                print(f'  Error processing {file_path}: {e}')

    # Final commit
    conn.commit()

    # Verify count
    cursor.execute('SELECT COUNT(*) FROM thumbImages')
    db_count = cursor.fetchone()[0]

    print(f"\n=== Summary ===")
    print(f"Files processed: {count}")
    print(f"Errors: {errors}")
    print(f"Database count: {db_count}")

    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    load_thumbnails()

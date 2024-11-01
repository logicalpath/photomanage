import sqlite3
import re

def extract_and_add_filenames():
    # Connect to the SQLite database
    conn = sqlite3.connect('mediameta.db')  # Replace with your actual database name
    cursor = conn.cursor()

    try:
        # Check if the ExtractedFilename column already exists
        cursor.execute("PRAGMA table_info(thumberrs)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'ExtractedFilename' not in columns:
            # Add the new column if it doesn't exist
            cursor.execute("ALTER TABLE thumberrs ADD COLUMN ExtractedFilename TEXT")
            print("Added new column 'ExtractedFilename' to the thumberrs table.")

        # Query to select the id and File columns from the thumberrs table
        query = "SELECT id, File FROM thumberrs"
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()

        for row in rows:
            row_id, file_path = row
            
            # Check if the file path contains "/Volumes"
            if "/Volumes" in file_path:
                # Use regex to find the filename after 'uuid' up to the file extension
                match = re.search(r'/uuid/.*?([^/]+\.[^/:]+)', file_path)
                
                if match:
                    filename = match.group(1)
                    # Update the row with the extracted filename
                    update_query = "UPDATE thumberrs SET ExtractedFilename = ? WHERE id = ?"
                    cursor.execute(update_query, (filename, row_id))
                    print(f"Updated row {row_id} with filename: {filename}")
                else:
                    print(f"No filename found after 'uuid' in row {row_id}")
            else:
                print(f"No '/Volumes' found in row {row_id}")

        # Commit the changes
        conn.commit()
        print("All changes have been committed to the database.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        print("Changes have been rolled back due to an error.")

    finally:
        conn.close()
        print("Database connection closed.")

# Run the function
extract_and_add_filenames()
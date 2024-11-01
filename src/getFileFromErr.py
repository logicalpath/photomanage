import sqlite3
import re

def extract_filenames():
    # Connect to the SQLite database
    conn = sqlite3.connect('mediameta.db')  # Replace with your actual database name
    cursor = conn.cursor()

    # Query to select the File column from the thumberrs table
    query = "SELECT File FROM thumberrs"

    try:
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()

        for row in rows:
            file_path = row[0]
            
            # Check if the file path contains "/Volumes"
            if "/Volumes" in file_path:
                # Use regex to find the filename after 'uuid'
                match = re.search(r'/uuid/.*?([^/]+\.[^/:]+)', file_path)
                
                if match:
                    filename = match.group(1)
                    print(f"Extracted filename: {filename}")
                else:
                    print(f"No filename found after 'uuid' in: {file_path}")
            else:
                print(f"No '/Volumes' found in: {file_path}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()

# Run the function
extract_filenames()
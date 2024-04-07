import sqlite3
import pickle
import sys

def check_columns_in_database(pickle_file_path, database_name, table_name, ignore_column=None):
    """
    Reads column information from a pickle file and checks if the specified columns in the database
    contain all blanks or nulls, ignoring the specified column number if provided.
    
    Parameters:
    - pickle_file_path: The file path to the pickle file containing the column information.
    - database_name: The name of the SQLite database to check.
    - table_name: The name of the table to check within the database.
    - ignore_column: (Optional) The column number to ignore when checking for null or blank entries.
    
    Prints:
    - Columns that contain no data (all values are blanks or nulls), excluding the ignored column if specified.
    """
    with open(pickle_file_path, 'rb') as file:
        columns_info = pickle.load(file)

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    column_results = {}
    counts = {}

    for i, column_details in enumerate(columns_info, start=1):
        if ignore_column is not None and i == ignore_column:
            continue

        column_name = column_details[1]  # Assuming the column name is in the second position

        query = f"""SELECT EXISTS(SELECT 1 FROM "{table_name}" WHERE TRIM("{column_name}") != '' OR "{column_name}" IS NOT NULL LIMIT 1)"""

        try:
            cursor.execute(query)
            exists_non_empty_or_non_null = cursor.fetchone()[0]
            column_results[column_name] = exists_non_empty_or_non_null == 0
        except sqlite3.OperationalError as e:
            print(f"Error in query for column '{column_name}': {e}")
            column_results[column_name] = 'Error'

    conn.close()

    # Filter and print columns that contain no data
    no_data_columns = [column for column, result in column_results.items() if result]

    if no_data_columns:
        print("Columns that contain no data (all values are blanks or nulls), excluding the ignored column:")
        for column in no_data_columns:
            print(f"- {column}")
    else:
        print("All columns contain some data or were ignored.")

def count_non_blank_rows_in_database(pickle_file_path, database_name, table_name):
    """
    Reads column information from a pickle file and counts non-null and non-blank rows for the specified columns in the database.

    Parameters:
    - pickle_file_path: The file path to the pickle file containing the column information.
    - database_name: The name of the SQLite database to check.
    - table_name: The name of the table to check within the database.

    Prints:
    - Count of non-null and non-blank rows for each column.
    """
    with open(pickle_file_path, 'rb') as file:
        columns_info = pickle.load(file)
    
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    counts = {}
    
    for column_details in columns_info:
        column_name = column_details[1]  # Assuming the column name is in the second position
        query = f"""SELECT COUNT(*) FROM "{table_name}" WHERE TRIM("{column_name}") != '' AND "{column_name}" IS NOT NULL"""
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            counts[column_name] = count
        except sqlite3.OperationalError as e:
            print(f"Error in query for column '{column_name}': {e}")
            counts[column_name] = 'Error'
    
    conn.close()

    # Print count of non-null and non-blank rows for each column
    if counts:
        print("Count of non-null and non-blank rows for each column:")
        for column, count in counts.items():
            print(f"- {column}: {count}")
    else:
        print("No columns found or an error occurred.")


if __name__ == "__main__":
    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python script_name.py <pickle_file_path> <database_name> <table_name> [ignore_column]")
        sys.exit(1)

    # Extract the file path, database name, and table name from the command-line arguments
    pickle_file_path = sys.argv[1]
    database_name = sys.argv[2]
    table_name = sys.argv[3]

    # Check if the ignore_column argument is provided
    if len(sys.argv) == 5:
        try:
            ignore_column = int(sys.argv[4])
        except ValueError:
            print("Invalid ignore_column value. Please provide an integer.")
            sys.exit(1)
    else:
        ignore_column = None

    # Proceed to check columns in the database based on the pickle file
    check_columns_in_database(pickle_file_path, database_name, table_name, ignore_column)
    count_non_blank_rows_in_database(pickle_file_path, database_name, table_name)
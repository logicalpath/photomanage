import sqlite3
import sys
import pickle


def get_table_columns(database_name, table_name):
    """
    Function to retrieve column information for a specified table in a SQLite database.

    Parameters:
    - database_name: The name of the SQLite database.
    - table_name: The name of the table to retrieve columns for.

    Returns:
    - A list of tuples containing column details.
    """
    # Connect to the specified SQLite database
    conn = sqlite3.connect(database_name)
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Retrieve the list of all columns in the specified table
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns = cursor.fetchall()
    # find the nuber of rows in the table
    cursor.execute(f"SELECT count(*) FROM '{table_name}'")  
    rows = cursor.fetchall()
    print(f"Number of rows in the table: {rows[0][0]}")
    
    
    # Close the connection
    conn.close()
    
    return columns

if __name__ == "__main__":
    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <database_name> <table_name>")
        sys.exit(1)

    # Extract the database name and table name from the command-line arguments
    database_name = sys.argv[1]
    table_name = sys.argv[2]

    # Retrieve the table columns
    columns = get_table_columns(database_name, table_name)

    # Print the column details
    for col in columns:
        print(col)

    # Assuming `columns` is your tuple
    with open('columns.pickle', 'wb') as file:
        pickle.dump(columns, file)


import sqlite3
import sys
from datetime import datetime

date_formats = [
    "%Y:%m:%d %H:%M:%S",  # Format without UTC offset
    "%Y:%m:%d",  # Format with date only
    "%Y:%m:%d %H:%M:%S%z",  # Format with UTC offset
    "%Y:%m:%d %H:%M:%SZ"  # Format with 'Z' indicating UTC
]

def check_seconds(datetime_string):
    try:
        # Split the string into date and time parts
        date_string, time_string = datetime_string.split(" ")

        # Split the date part into year, month, and day
        year, month, day = date_string.split(":")

        # Split the time part into hour, minute, and second
        hour, minute, second = time_string.split(":")

        # Check the value of the second
        if 0 <= int(second) <= 59:
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False

def is_valid_date(date_string):
    for format in date_formats:
        try:
            datetime.strptime(date_string, format)
            return True
        except ValueError:
            pass
    return False

def find_invalid_entries(database, table, column):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    query = f"SELECT {column} FROM {table}"
    cursor.execute(query)

    invalid_entries = []
    for row in cursor.fetchall():
        date_string = row[0]
        if not is_valid_date(date_string):
            invalid_entries.append(date_string)

    conn.close()
    return invalid_entries

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <database> <table> <column>")
        sys.exit(1)

    database = sys.argv[1]
    table = sys.argv[2]
    column = sys.argv[3]

    invalid_entries = find_invalid_entries(database, table, column)
    output_file = table + column + ".out"

    with open(output_file, "w") as file:
        if invalid_entries:
            file.write("Invalid date entries found:\n")
            for entry in invalid_entries:
                file.write(entry + "\n")
        else:
            file.write("No invalid date entries found.")

print(f"Results written to {output_file}.")
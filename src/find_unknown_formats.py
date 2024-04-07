import sqlite3
import sys
from datetime import datetime
import calendar


date_formats = [
"%Y:%m:%d %H:%M:%S", # Format without UTC offset
"%Y:%m:%d", # Format with date only
"%Y:%m:%d %H:%M:%S%z", # Format with UTC offset
"%Y:%m:%d %H:%M:%SZ", # Format with 'Z' indicating UTC
"%Y:%m:%d %H:%M:%S.%fZ", # Format with fractional seconds and 'Z' indicating UTC
]


def correct_date(datetime_string):
    try:
        # Split the string into date and time parts
        date_string, time_string = datetime_string.split(" ")

        # Split the date part into year, month, and day
        year, month, day = date_string.split(":")

        # Split the time part into hour, minute, and second
        hour, minute, second = time_string.split(":")

        # Check if all components are zero
        if all(int(component) == 0 for component in [year, month, day, hour, minute, second]):
            # Set a default valid date and time
            return "1970:01:01 00:00:00"
            
        # Check if the year is a valid integer
        if not isinstance(year, int):
            return False
         # Check if the month is a valid integer between 1 and 12
        if not isinstance(month, int) or month < 1 or month > 12:
            return False
        # Check if the day is a valid integer between 1 and the maximum days in the month
        max_days = calendar.monthrange(year, month)[1]
        if not isinstance(day, int) or day < 1 or day > max_days:
            # Set the day to "01" if it is not valid
             corrected_date = f"{year}:{month}:01"
             corrected_datetime = f"{corrected_date} {time_string}"
             return corrected_datetime    

        # Check the value of the second
        if 0 <= int(second) <= 59:
            return datetime_string
        else:
            # Set the seconds to "00" if they are not valid
            corrected_time = f"{hour}:{minute}:00"
            corrected_datetime = f"{date_string} {corrected_time}"
            return corrected_datetime
    except (ValueError, TypeError):
        return None

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
            corrected_date = correct_date(date_string)
            if corrected_date:
                if is_valid_date(corrected_date):
                    print(f"Corrected invalid date: {date_string} to {corrected_date}")
                    query = f"UPDATE {table} SET {column} = ? WHERE {column} = ?"
                    cursor.execute(query, (corrected_date, date_string))
                    conn.commit()
                else:
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
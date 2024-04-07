from datetime import datetime

def convert(value):
    date_formats = [
        "%Y:%m:%d %H:%M:%S",    # Format without UTC offset
        "%Y:%m:%d",             # Format with date only
        "%Y:%m:%d %H:%M:%S%z",  # Format with UTC offset
        "%Y:%m:%d %H:%M:%SZ"   # Format with 'Z' indicating UTC
    ]

    if not value.strip():
        # Handle the empty date string case
        print("Date string is empty.")
        parsed_date = None  # Or any appropriate default value or action
    else:
        parsed_date = None
        for date_format in date_formats:
            try:
                # Attempt to parse the date string using the current format
                parsed_date = datetime.strptime(value, date_format)
                print(f"Successfully parsed date using format: {date_format}")
                break  # If parsing succeeds, exit the loop
            except ValueError as e:
                print (f"Error parsing date: {e}")
                pass  # If parsing fails, continue to the next format

        if parsed_date is None:
            # Handle the case where none of the formats matched
            print("Error parsing date: No matching format found.")

    return parsed_date
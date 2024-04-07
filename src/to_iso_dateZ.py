from datetime import datetime

def convert(value):

    date_format = "%Y:%m:%d %H:%M:%S"
    date_format_with_offset = f"{date_format}%z"
    date_format_ymd = "%Y:%m:%d"


    if not value.strip():
        # Handle the empty date string case
        print("Date string is empty.")
        parsed_date = None  # Or any appropriate default value or action
    else:
        try:
            # Attempt to parse the date string
            parsed_date = datetime.strptime(value, date_format_with_offset)
        except ValueError as e:
            # Handle the case where the date is invalid
            print(f"Error parsing date: {e}")
            parsed_date = None

    return parsed_date

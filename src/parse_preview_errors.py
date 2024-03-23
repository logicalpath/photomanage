import csv
import sys

def process_entries(input_file_path):
    entries = []  # List to hold all entries, each entry is a tuple (File, Error)
    current_entry = []
    error_part = []
    collecting_error = False

    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("Error creating preview"):
                # Start of a new entry, save previous one if it exists
                if current_entry or error_part:
                    entries.append(("\n".join(current_entry), "\n".join(error_part)))
                    current_entry = []
                    error_part = []
                collecting_error = False
            elif "Stream mapping:" in line:
                collecting_error = True
            
            if collecting_error:
                error_part.append(line.rstrip())  # Keep line breaks
            else:
                current_entry.append(line.rstrip())  # Keep line breaks

            if line.strip() == "Conversion failed!":
                collecting_error = False
                # End of an entry, prepare to start a new one
                entries.append(("\n".join(current_entry), "\n".join(error_part)))
                current_entry = []
                error_part = []

    # Check for any remaining entry not appended due to missing "Conversion failed!"
    if current_entry or error_part:
        entries.append(("\n".join(current_entry), "\n".join(error_part)))

    return entries

def create_csv(input_file_path, entries):
    output_file_path = input_file_path.rsplit('.', 1)[0] + '.csv'

    with open(output_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['File', 'Error'])  # Writing the header
        for file_entry, error_entry in entries:
            writer.writerow([file_entry, error_entry])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    entries = process_entries(input_file_path)
    create_csv(input_file_path, entries)
    print(f"CSV file has been created based on {input_file_path}")

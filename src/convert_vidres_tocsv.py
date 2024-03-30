import csv
import sys

# Function to parse the input text and extract file information
def parse_input_text(input_text):
    lines = input_text.strip().split("\n")
    file_info = []
    current_info = {}
    for line in lines:
        if line.startswith("File:"):
            if current_info:
                file_info.append(current_info)
                current_info = {}
            current_info["File"] = line.split(":", 1)[1].strip()
        elif line.startswith("width="):
            current_info["Width"] = line.split("=", 1)[1].strip()
        elif line.startswith("height="):
            current_info["Height"] = line.split("=", 1)[1].strip()
    if current_info:
        file_info.append(current_info)
    return file_info

def main(input_file_name):
    # Read the input file
    with open(input_file_name, 'r') as file:
        input_text = file.read()

    # Parse the input text
    file_info = parse_input_text(input_text)

    # Construct the output CSV file name
    output_file_name = input_file_name.rsplit('.', 1)[0] + '.csv'

    # Write to the CSV file
    with open(output_file_name, 'w', newline='') as csvfile:
        fieldnames = ["File", "Width", "Height"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(file_info)

    print(f"CSV file '{output_file_name}' has been created.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file_name>")
    else:
        main(sys.argv[1])

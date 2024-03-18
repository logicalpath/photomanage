import re
import csv
import os
import sys

def parse_errors_to_csv(input_file_path, output_folder):
    # Regular expression patterns to match file paths and file type info
    file_path_pattern = r"Error creating thumbnail for (.*): cannot identify image file"
    file_type_info_pattern = r"File type info: (.*): (.*)"
    
    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Extract the base name of the input file and replace its extension with '.csv'
    input_file_base_name = os.path.basename(input_file_path)
    output_file_name = os.path.splitext(input_file_base_name)[0] + ".csv"

    # Define the output CSV file path
    output_file_path = os.path.join(output_folder, output_file_name)

    # Lists to hold parsed data
    files = []
    file_infos = []

    # Read the input file and extract required information
    with open(input_file_path, 'r') as file:
        for line in file:
            file_path_match = re.search(file_path_pattern, line)
            file_type_info_match = re.search(file_type_info_pattern, line)
            if file_path_match:
                files.append(file_path_match.group(1))
            elif file_type_info_match:
                # Extract only the file type info, excluding the file name
                file_infos.append(file_type_info_match.group(2))

    # Write the extracted information to a CSV file
    with open(output_file_path, 'w', newline='') as csvfile:
        fieldnames = ['File', 'File type Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for file, info in zip(files, file_infos):
            writer.writerow({'File': file, 'File type Info': info})

    print(f"CSV file has been created at {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: script.py <input_file_path> <output_folder>")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    output_folder = sys.argv[2]
    
    parse_errors_to_csv(input_file_path, output_folder)

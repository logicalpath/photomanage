import csv
import re
import argparse
import os

def parse_error_log_to_csv_modified(error_log_path, csv_output_path):
    with open(error_log_path, 'r') as file:
        lines = file.readlines()

    records = []
    i = 0
    while i < len(lines):
        # Extracting the file name from the conversion error
        conversion_error_match = re.search(r"Conversion error for (.+):", lines[i].strip())
        conversion_error = conversion_error_match.group(1) if conversion_error_match else ""
        
        imagemagick_error = lines[i + 1].strip() if i + 1 < len(lines) else ""
        file_type = lines[i + 3].strip() if i + 3 < len(lines) else ""
        
        records.append([conversion_error, imagemagick_error, file_type])
        i += 4

    with open(csv_output_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Conversion Error", "ImageMagick error", "File type"])
        csvwriter.writerows(records)

def main():
    parser = argparse.ArgumentParser(description='Parse an error log and convert it to a CSV file.')
    parser.add_argument('error_log_file', type=str, help='Path to the error log file.')
    parser.add_argument('output_file', type=str, nargs='?', help='Path to the output CSV file.', default=None)
    
    args = parser.parse_args()
    
    # If output file is not provided, default it to the same name as the input file but with a .csv extension
    if args.output_file is None:
        base_name = os.path.splitext(args.error_log_file)[0]
        args.output_file = f"{base_name}.csv"
    
    # Parsing the error log with the modified criteria and generating the CSV
    parse_error_log_to_csv_modified(args.error_log_file, args.output_file)

if __name__ == '__main__':
    main()

import csv
import sys

def process_file(input_file, output_csv):
    with open(input_file, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        # Write the header
        csv_writer.writerow(['Directory', 'File'])

        for line in infile:
            line = line.strip()
            if line:
                # Extract the first three characters for the directory
                directory = line[:3]
                # Extract everything from the fifth character onward for the file
                # ignore / at the beginning
                file_name = line[4:]
                csv_writer.writerow([directory, file_name])

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_csv = sys.argv[2]
    process_file(input_file, output_csv)

if __name__ == "__main__":
    main()

import sys
import os
import csv

def create_csv_file(input_file):
    csv_file = os.path.splitext(input_file)[0] + '.csv'
    
    with open(input_file, 'r') as file_in, open(csv_file, 'w', newline='') as file_out:
        writer = csv.writer(file_out)
        writer.writerow(['FileName', 'FileSize'])
        
        for line in file_in:
            parts = line.strip().split()
            if len(parts) >= 2:
                file_name = ' '.join(parts[:-1])
                file_size = parts[-1]
                writer.writerow([file_name, file_size])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    create_csv_file(input_file)
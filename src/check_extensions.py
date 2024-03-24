import csv
import sys

def check_file_extensions(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            old_name_ext = row['Old Name'].split('.')[-1]
            new_name_ext = row['New Name'].split('.')[-1]
            if old_name_ext != new_name_ext:
                print(f"Row {row['rowid']}: Extension mismatch between {row['Old Name']} and {row['New Name']}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file_path>")
    else:
        csv_file_path = sys.argv[1]
        check_file_extensions(csv_file_path)

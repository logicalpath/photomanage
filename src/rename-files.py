import os
import uuid
import csv
import sys

def rename_files_in_directory(directory_path):
    old_new_name_map = {}

    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)):
            new_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
            os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_filename))
            old_new_name_map[filename] = new_filename

    return old_new_name_map

def write_mapping_to_csv(mapping, csv_file_path):
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Old Name', 'New Name'])
        for old_name, new_name in mapping.items():
            writer.writerow([old_name, new_name])

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]

    if not os.path.isdir(directory_path):
        print(f"The provided directory does not exist: {directory_path}")
        sys.exit(1)

    mapping = rename_files_in_directory(directory_path)
    #csv_file_path = os.path.join(directory_path, 'filename_mapping.csv')
    csv_file_path = os.path.join(directory_path, directory_path.split(os.sep)[-1] + '-mapping.csv')
    write_mapping_to_csv(mapping, csv_file_path)

    print(f"Renaming completed. Mapping saved to {csv_file_path}.")

if __name__ == "__main__":
    main()

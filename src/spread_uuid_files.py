import os
import sys
import shutil
import uuid

def main():
    # Check if two arguments are given
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <source_directory> <destination_directory>")
        sys.exit(1)

    # Get the source and destination directories from the script's arguments
    src_dir = sys.argv[1]
    dest_base_dir = sys.argv[2]

    # Check if the provided source directory exists
    if not os.path.isdir(src_dir):
        print(f"Error: Source directory {src_dir} does not exist.")
        sys.exit(1)

    # Loop over files in the source directory
    for file in os.listdir(src_dir):
        file_path = os.path.join(src_dir, file)
        if os.path.isfile(file_path):
            # Generate a unique filename
            unique_filename = str(uuid.uuid4())

            # Get the file extension
            _, file_extension = os.path.splitext(file)

            # Append the extension to the unique filename
            unique_filename_with_ext = unique_filename + file_extension

            # Determine the first letter of the UUID and the destination directory
            first_letter = unique_filename[0]
            dest_dir = os.path.join(dest_base_dir, first_letter)

            # Create the destination directory if it doesn't exist
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            dest_file_path = os.path.join(dest_dir, unique_filename_with_ext)

            # Ensure the UUID file does not already exist in the destination directory
            while os.path.exists(dest_file_path):
                unique_filename = str(uuid.uuid4())
                unique_filename_with_ext = unique_filename + file_extension
                dest_file_path = os.path.join(dest_dir, unique_filename_with_ext)

            # Move and rename the file to the new directory with a unique name
            shutil.move(file_path, dest_file_path)

if __name__ == "__main__":
    main()

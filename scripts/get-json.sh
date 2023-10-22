#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_zip_file> <destination_directory>"
    exit 1
fi

# Variables
ZIP_FILE="$1"
DEST_DIR="$2"

# Ensure the destination directory exists
mkdir -p "$DEST_DIR"

# Extract .json files and create necessary subdirectories
unzip -l "$ZIP_FILE" | grep '\.json$' | awk '{$1=$2=$3=""; print $0}' | sed 's/^ *//' | while read -r file_path; do
    # Extract the immediate parent directory from the file path
    parent_dir=$(basename "$(dirname "$file_path")")

    # Create a directory under DEST_DIR if it doesn't exist
    mkdir -p "$DEST_DIR/$parent_dir"

    # Extract the .json file into the created directory
    unzip -j "$ZIP_FILE" "$file_path" -d "$DEST_DIR/$parent_dir"
done

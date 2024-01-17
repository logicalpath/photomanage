#!/bin/bash

# Check if two arguments are given
if [ $# -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

# Get the source and destination directories from the script's arguments
SRC_DIR=$1
DEST_DIR=$2

# Check if the source directory exists
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: Source directory $SRC_DIR does not exist."
    exit 1
fi

# Check if the destination directory exists, create it if not
if [ ! -d "$DEST_DIR" ]; then
    echo "Destination directory $DEST_DIR does not exist. Creating it."
    mkdir -p "$DEST_DIR"
fi

echo "File count prior to move:  "
find "$DEST_DIR" -type f ! -path '*/.*' | wc -l
echo


# Loop over files in the source directory
for file in "$SRC_DIR"/*; do
    if [[ -f $file ]]; then
        # Extract the first letter of the filename
        FOLDER=$(basename "$file" | cut -c1)
        # Create a directory in the destination directory if it doesn't exist
        NEW_DIR="$DEST_DIR/$FOLDER"
        mkdir -p "$NEW_DIR"
        # Move the file
        mv "$file" "$NEW_DIR/"
    fi
done

echo "File count after move:  "
find "$DEST_DIR" -type f ! -path '*/.*' | wc -l
echo
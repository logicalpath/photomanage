#!/bin/bash

# Check if an argument is given
if [ $# -eq 0 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Get the directory from the script's first argument
DIR=$1

# Check if the provided directory exists
if [ ! -d "$DIR" ]; then
    echo "Error: Directory $DIR does not exist."
    exit 1
fi

# Get the parent directory of DIR
PARENT_DIR=$(dirname "$DIR")

# Loop over files
for file in "$DIR"/*; do
    if [[ -f $file ]]; then
        # Extract the first letter of the filename
        FOLDER=$(basename "$file" | cut -c1)
        # Create a directory at the same level as DIR if it doesn't exist
        NEW_DIR="$PARENT_DIR/$FOLDER"
        mkdir -p "$NEW_DIR"
        # Move the file
        mv "$file" "$NEW_DIR/"
    fi
done

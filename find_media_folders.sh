#!/bin/bash

# Path to the top-level directory
TOP_DIR=$1
echo "Searching $TOP_DIR for media files..."

folder=$(./get-basename.sh "$1")
echo "The extracted folder name is: $folder"

output_file="$folder-output.csv"
exclude_file="$folder-exclusions.csv"
json_file="$folder-json.csv"

echo "Output file: $output_file"

# If output_file or exclude_file exists, remove them to start fresh
if [ -f "$output_file" ]; then
    rm "$output_file"
fi

if [ -f "$exclude_file" ]; then
    rm "$exclude_file"
fi
if [ -f "$json_file" ]; then
    rm "$json_file"
fi

# Define the file extensions to search for (simplified and all in lowercase)
EXTENSIONS="(\.jpeg|\.jpg|\.nef|\.png|\.mov|\.mp4|\.3g2|\.3gp|\.aae|\.avi|\.gif|\.heic|\.m4v|\.mpg|\.pdf|\.psd|\.tiff|\.tif)$"
JSON_EXTENSION="\.json$"

# Adding the header row to the CSV
echo "Directory,File,FileSize" > "$output_file"

# Search for media files within the TOP_DIR and its subdirectories
find "$TOP_DIR" -type f | while IFS= read -r filepath; do
    # Check if the file matches the desired extensions using case-insensitive matching
    if echo "$filepath" | grep -iE "$EXTENSIONS" &>/dev/null; then
        dir=$(dirname "$filepath")
        file=$(basename "$filepath")
        # Get the file size using stat command
        filesize=$(stat -f %z "$filepath")
        echo "$dir,$file,$filesize" >> "$output_file"
    # Check if the file is a .json file
    elif echo "$filepath" | grep -iE "$JSON_EXTENSION" &>/dev/null; then
        echo "$filepath" >> "$json_file"
    else
        echo "$filepath" >> "$exclude_file"
    fi
done


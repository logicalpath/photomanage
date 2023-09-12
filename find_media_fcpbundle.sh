#!/bin/bash

# Path to the top-level directory
TOP_DIR=$1
echo "Searching $TOP_DIR for apple movie media files..."

folder=$(./get-basename.sh "$1")
echo "The extracted folder name is: $folder"

output_file="$folder-output.csv"
exclude_file="$folder-exclusions.csv"

echo "Output file: $output_file"

# If output_file or exclude_file exists, remove them to start fresh
if [ -f "$output_file" ]; then
    rm "$output_file"
fi

if [ -f "$exclude_file" ]; then
    rm "$exclude_file"
fi

# Define the file extensions to search for (simplified and all in lowercase)
EXTENSIONS="(\.jpeg|\.jpg|\.nef|\.png|\.mov|\.mp4|\.3g2|\.3gp|\.aae|\.avi|\.gif|\.heic|\.m4v|\.mpg|\.pdf|\.psd|\.tiff)$"

# Adding the header row to the CSV
echo "Directory,File,FileSize" > "$output_file"

# Find directories with ".fcpbundle" in their name
find "$TOP_DIR" -type d -name "*.fcpbundle" | while IFS= read -r fcpbundle_dir; do
    # From there, search for media files within subdirectories
    find "$fcpbundle_dir" -type f -depth | while IFS= read -r filepath; do
        # Check if the file matches the desired extensions using case-insensitive matching
        if echo "$filepath" | grep -iE "$EXTENSIONS" &>/dev/null; then
            dir=$(dirname "$filepath")
            file=$(basename "$filepath")
            # Get the file size using stat command
            filesize=$(stat -f %z "$filepath")
            echo "$dir,$file,$filesize" >> "$output_file"
        else
            echo "$filepath" >> "$exclude_file"
        fi
    done
done

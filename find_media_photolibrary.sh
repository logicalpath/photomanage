
#!/bin/bash

# Path to the top-level directory
TOP_DIR=$1
echo "Searching $TOP_DIR for media files..."

# If photolib-output.csv or photolib-exclusions.csv exists, remove them to start fresh
[ -f photolib-output.csv ] && rm photolib-output.csv
[ -f photolib-exclusions.csv ] && rm photolib-exclusions.csv

# Define the file extensions to search for (simplified and all in lowercase)
EXTENSIONS="(\.jpeg|\.jpg|\.nef|\.png|\.mov|\.mp4|\.3g2|\.3gp|\.aae|\.avi|\.gif|\.heic|\.m4v|\.mpg|\.pdf|\.psd|\.tiff)$"

# Find directories with ".photoslibrary" in their name
find "$TOP_DIR" -type d -name "*.photoslibrary" | while IFS= read -r photoslibrary_dir; do
    # From there, search for media files within the "originals" subdirectory
    find "$photoslibrary_dir/originals" -type f | while IFS= read -r filepath; do
        # Check if the file matches the desired extensions using case-insensitive matching
        if echo "$filepath" | grep -iE "$EXTENSIONS" &>/dev/null; then
            dir=$(dirname "$filepath")
            file=$(basename "$filepath")
            echo "$dir,$file" >> photolib-output.csv
        else
            echo "$filepath" >> photolib-exclusions.csv
        fi
    done
done

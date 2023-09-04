
#!/bin/bash

# Path to the top-level directory
TOP_DIR=$1
echo "Searching $TOP_DIR for media files..."

# If gphoto-output.csv or gphoto-exclusions.csv exists, remove them to start fresh
[ -f gphoto-output.csv ] && rm gphoto-output.csv
[ -f gphoto-exclusions.csv ] && rm gphoto-exclusions.csv
[ -f gphoto-json.csv ] && rm gphoto-json.csv


# Define the file extensions to search for (simplified and all in lowercase)
EXTENSIONS="(\.jpeg|\.jpg|\.nef|\.png|\.mov|\.mp4|\.3g2|\.3gp|\.aae|\.avi|\.gif|\.heic|\.m4v|\.mpg|\.pdf|\.psd|\.tiff|\.tif)$"
JSON_EXTENSION="\.json$"

# Search for media files within the TOP_DIR and its subdirectories
find "$TOP_DIR" -type f | while IFS= read -r filepath; do
    # Check if the file matches the desired extensions using case-insensitive matching
    if echo "$filepath" | grep -iE "$EXTENSIONS" &>/dev/null; then
        dir=$(dirname "$filepath")
        file=$(basename "$filepath")
        echo "$dir,$file" >> gphoto-output.csv
    # Check if the file is a .json file
    elif echo "$filepath" | grep -iE "$JSON_EXTENSION" &>/dev/null; then
        echo "$filepath" >> gphoto-json.csv
    else
        echo "$filepath" >> gphoto-exclusions.csv
    fi
done


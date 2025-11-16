#!/bin/bash

# Script to extract image dimensions from media files
# Usage: ./getImageDimensions.sh <directory-path>

# Check if exiftool is installed
if ! command -v exiftool &> /dev/null; then
    echo "Error: exiftool is not installed."
    echo "Please install exiftool to use this script."
    exit 1
fi

# Check if a directory argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No directory specified."
    echo "Usage: $0 <directory-path>"
    exit 1
fi

# Path to the top-level directory
TOP_DIR=$1

# Verify that the provided path exists and is a directory
if [ ! -d "$TOP_DIR" ]; then
    echo "Error: Directory '$TOP_DIR' does not exist."
    exit 1
fi

echo "Extracting image dimensions from $TOP_DIR..."

# Output file
OUTPUT_FILE="image-dimensions.csv"

echo "Output file: $OUTPUT_FILE"

# If output file exists, remove it to start fresh
if [ -f "$OUTPUT_FILE" ]; then
    rm "$OUTPUT_FILE"
fi

# Extract image dimensions using exiftool
# -csv: Output in CSV format
# -FileName: Get the filename
# -ImageWidth: Get the image width
# -ImageHeight: Get the image height
# -n: No print conversion (get numeric values)
# ! -name '._*': Ignore Apple resource fork files
find "$TOP_DIR" -type f ! -name '._*' -exec exiftool -csv -FileName -ImageWidth -ImageHeight -n {} + > "$OUTPUT_FILE"

echo "Extraction complete. Output saved to $OUTPUT_FILE"

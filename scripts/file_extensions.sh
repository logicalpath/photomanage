#!/bin/bash

# Script to find and record all file extensions in and below the current directory

# Output file for the extensions
OUTPUT_FILE="file_extensions.txt"

# Check if the output file already exists, and remove it to start fresh
if [ -f "$OUTPUT_FILE" ]; then
    rm "$OUTPUT_FILE"
fi

# Find all files, extract their extensions, sort them, get unique entries, and then save to the output file
find . -type f | sed 's/.*\.//' | sort | uniq > "$OUTPUT_FILE"

echo "All unique file extensions have been recorded in $OUTPUT_FILE"

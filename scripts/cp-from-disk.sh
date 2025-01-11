#!/bin/bash

# Check if source directory is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 SOURCE_DIR"
    exit 1
fi

# Store source directory from command line
SOURCE_DIR="$1"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Create destination directory name with current date/time
DEST_DIR=$(date +"%Y%m%d_%H%M%S")

# Create the directory
mkdir "$DEST_DIR"

# Copy files with metadata
exiftool -tagsFromFile @ -all:all "-Directory=./$DEST_DIR" "$SOURCE_DIR"
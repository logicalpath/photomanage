#!/bin/bash

# Check if both source and output directories are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 SOURCE_DIR OUTPUT_DIR"
    exit 1
fi

# Store source and output directories from command line
SOURCE_DIR="$1"
OUTPUT_DIR="$2"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Check if output directory exists, create it if it doesn't
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
fi

# Create destination directory name with current date/time
DEST_DIR=$(date +"%Y%m%d_%H%M%S")
FULL_DEST_DIR="$OUTPUT_DIR/$DEST_DIR"

# Create the destination directory
mkdir "$FULL_DEST_DIR"

# Copy files with metadata
exiftool -tagsFromFile @ -all:all "-Directory=$FULL_DEST_DIR" "$SOURCE_DIR"
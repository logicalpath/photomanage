#!/bin/bash

# Ensure the first argument is 'folder' or 'photolib'
if [ "$1" != "folder" ] && [ "$1" != "photolib" ]; then
    echo "Error: First argument should be either 'folder' or 'photolib'"
    exit 1
fi

# Path to the top-level directory
TOP_DIR=$2
echo "Searching $TOP_DIR for media files..."

folder=$(./get-basename.sh "$2")
echo "The extracted folder name is: $folder"

exif_file="$folder-exif.csv"


echo "Exif file: $exif_file"

# If output_file or exclude_file exists, remove them to start fresh
if [ -f "exif_file" ]; then
    rm "$exif_file"
fi
 
echo "Full Directory = $TOP_DIR"
echo "exif_file = $exif_file"

# Decide which exiftool command to run based on the first argument
if [ "$1" == "folder" ]; then
    exiftool -csv -"*GPS*" -"Date*" -r --ext json "$TOP_DIR" > "$exif_file"
else
    find "$TOP_DIR" -type d -name 'originals' -exec exiftool -csv -"*GPS*" -"Date*" -r --ext ^json {} + > "$exif_file"
fi
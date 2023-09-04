#!/bin/bash

# Path to the top-level directory
TOP_DIR=$1
echo "Searching $TOP_DIR for media files..."

folder=$(./get-basename.sh "$1")
echo "The extracted folder name is: $folder"

exif_file="$folder-exif.csv"


echo "Exif file: $exif_file"

# If output_file or exclude_file exists, remove them to start fresh
if [ -f "exif_file" ]; then
    rm "$exif_file"
fi
 
echo "Full Directory = $TOP_DIR"
echo "exif_file = $exif_file"

# This works where '.' is the current directory
# -r means recursive
exiftool -csv -"*GPS*" -"Date*" -r --ext json $TOP_DIR > $exif_file


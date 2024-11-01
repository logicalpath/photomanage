#!/bin/bash

# Check if a directory argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No directory specified."
    echo "Usage: $0 <directory-path>"
    exit 1
fi

# Path to the top-level directory
TOP_DIR=$1
echo "Searching $TOP_DIR for media files..."

folder=$(./get-basename.sh "$1")
echo "The extracted folder name is: $folder"

exif_file="$folder/exifMore.csv"

echo "Exif file: $exif_file"

# If exif file exists, remove it to start fresh
if [ -f "exif_file" ]; then
    rm "$exif_file"
fi
 
echo "Full Directory = $TOP_DIR"
echo "exif_file = $exif_file"


# grab filename without path
# find "$TOP_DIR" -type f ! -name '._*' -exec exiftool -csv -"Create*Date" -"Date*Created" -"Profile*Date*Time" -n -gpslatitude -gpslongitude -filename {} + > "$exif_file"
find "$TOP_DIR" -type f ! -name '._*' -exec exiftool -csv -ImageSize -Megapixels -time:all -gps:all -a -s -filename {} + > "$exif_file"



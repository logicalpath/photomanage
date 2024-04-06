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

# exif_file="$folder-exif.csv"
exif_file="$folder/exif.csv"

echo "Exif file: $exif_file"

# If exif file exists, remove it to start fresh
if [ -f "exif_file" ]; then
    rm "$exif_file"
fi
 
echo "Full Directory = $TOP_DIR"
echo "exif_file = $exif_file"


# ignore ._03fd20b0-483e-452d-88fc-89720a36c172.JPG
# find "$TOP_DIR" -type f ! -name '._*' -exec exiftool -csv -"Create*Date" -n -gpslatitude -gpslongitude {} + > "$exif_file"
# grab filename without path
find "$TOP_DIR" -type f ! -name '._*' -exec exiftool -csv -"Create*Date" -"Date*Created" -"Profile*Date*Time" -"DateTimeOriginal" -"ModifyDate" -"PreviewDate" -'GPSDateStamp' -'GPSDateTime' -n -gpslatitude -gpslongitude -filename {} + > "$exif_file"

#exiftool -csv -"Create*Date" -n -gpslatitude -gpslongitude -r --ext json "$TOP_DIR" > "$exif_file"


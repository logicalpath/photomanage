#!/bin/bash

# Shell script to create thumbnails for image files using ImageMagick

# Usage: ./script.sh <input_directory> <output_directory> [<resize_dimensions>] [<max_thumbnails>] [<error_log>]
# Example: ./script.sh ./input ./output "256x256" 100 "errors.log"

input_directory=$1
output_directory=$2
resize_dimensions=${3:-"128x128"} # Default is 128x128 if not specified
max_thumbnails=${4:-0} # Default is 0, meaning no limit
error_log=${5:-"error_log.txt"}

# Ensure output directory exists
mkdir -p "$output_directory"

# Ensure the error log file is empty
> "$error_log"

# Supported image extensions (in lowercase)
extensions="heic jpg nef png aae jpeg tif tiff"

# Counter for created thumbnails
count=0

# Function to create a thumbnail
create_thumbnail() {
    local input_path="$1"
    local output_path="$2"
    
    if magick "$input_path" -resize "$resize_dimensions" "$output_path"; then
    # if convert "$input_path" -resize "$resize_dimensions" "$output_path"; then
        echo "Thumbnail created for $input_path"
    else
        echo "Error creating thumbnail for $input_path" >> "$error_log"
        file "$input_path" >> "$error_log"
    fi
}

# Find and process image files
find "$input_directory" -type f | while read -r file; do
    # Check if we reached the maximum number of thumbnails (if set)
    if [[ $max_thumbnails -ne 0 ]] && [[ $count -ge $max_thumbnails ]]; then
        break
    fi
    
    # Convert the file extension to lowercase for comparison
    extension="${file##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')  # Convert to lowercase using tr
    
    if [[ $extensions =~ $extension ]]; then
        filename=$(basename "$file")
        output_file="$output_directory/$filename"
        create_thumbnail "$file" "$output_file"
        ((count++))
    fi
done

echo "Process completed. $count thumbnails created."

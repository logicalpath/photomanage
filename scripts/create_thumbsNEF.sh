#!/bin/bash

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_directory> <output_directory> [<resize_dimensions>] [<max_thumbnails>] [<error_log>]"
    exit 1
fi

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
extensions="heic jpg png aae jpeg tif tiff"  # Removed raw formats as they're handled separately
raw_formats="nef arw"  # RAW formats we handle specially

# Counter for created thumbnails
count=0

# Function to create a thumbnail
create_thumbnail() {
    local input_path="$1"
    local output_path="$2"
    local extension="${input_path##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')  # Convert to lowercase
    
    if [[ " $raw_formats " =~ " $extension " ]]; then
        # Direct dcraw extraction and conversion for RAW files
        if dcraw -e "$input_path" && \
           mv "${input_path%.*}.thumb.jpg" "$output_path"; then
            echo "Thumbnail created for $input_path"
            return 0
        else
            echo "Error creating thumbnail for $input_path" >> "$error_log"
            file "$input_path" >> "$error_log"
            return 1
        fi
    else
        if magick "$input_path" -resize "$resize_dimensions" "$output_path"; then
            echo "Thumbnail created for $input_path"
            return 0
        else
            echo "Error creating thumbnail for $input_path" >> "$error_log"
            file "$input_path" >> "$error_log"
            return 1
        fi
    fi
}

# Function to process a directory
process_directory() {
    local current_dir="$1"
    
    # Process all files in the current directory
    for file in "$current_dir"/*; do
        # Skip if it's a directory that matches the output directory path
        if [[ -d "$file" ]]; then
            # Skip the output directory and its subdirectories
            if [[ "$file" != "$output_directory"* ]]; then
                process_directory "$file"
            fi
            continue
        fi
        
        # Skip if not a file
        [[ ! -f "$file" ]] && continue
        
        # Check if we reached the maximum number of thumbnails (if set)
        if [[ $max_thumbnails -ne 0 ]] && [[ $count -ge $max_thumbnails ]]; then
            return
        fi
        
        # Convert the file extension to lowercase for comparison
        extension="${file##*.}"
        extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')  # Convert to lowercase using tr
        
        if [[ " $raw_formats " =~ " $extension " ]] || [[ $extensions =~ $extension ]]; then
            filename=$(basename "$file")
            # Get first character of filename and ensure lowercase
            first_char=$(echo "${filename:0:1}" | tr '[:upper:]' '[:lower:]')
            
            # Create the output directory if it doesn't exist
            # Note: Removed the $first_char from the path
            mkdir -p "$output_directory"
            
            # Preserve the relative path structure after the input directory
            relative_path=${file#$input_directory/}
            relative_dir=$(dirname "$relative_path")
            
            # Create subdirectory in output directory to match input structure
            # Note: Removed the $first_char from the path
            mkdir -p "$output_directory/$relative_dir"
            
            if [[ " $raw_formats " =~ " $extension " ]]; then
                # Preserve original extension case for RAW files
                original_extension="${file##*.}"
                output_file="$output_directory/$relative_dir/${filename%.*}.$original_extension"
            else
                output_file="$output_directory/$relative_dir/${filename%.*}.jpg"
            fi
            
            if create_thumbnail "$file" "$output_file"; then
                ((count++))
            fi
        fi
    done
}

# Start processing from the input directory
process_directory "$input_directory"

echo "Process completed. $count thumbnails created."
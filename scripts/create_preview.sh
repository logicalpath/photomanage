#!/bin/bash

# Check if at least the minimum number of arguments was passed
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <input_dir> <output_dir> [max_previews]"
    exit 1
fi

# Assign command line arguments to variables
input_dir="$1"
output_dir="$2"
max_previews=${3:-0} # Default to 0, which means no maximum

# Define the video extensions to look for
extensions=("mp4" "mov" "avi" "mpg" "3gp" "m4v")

# Initialize counter
count=0

# Function to create previews
create_preview() {
    local input_file="$1"
    local output_file="$2"

    # Increment the counter
    ((count++))

    # Command to generate a video preview
    ffmpeg -i "$input_file" -ss 00:00:05 -t 00:00:10 -vf "scale=320:-1" -c:v libx264 -preset veryfast -crf 28 "$output_file"
}

# Loop through the specified extensions and find files
for ext in "${extensions[@]}"; do
    find "$input_dir" -type f -name "*.$ext" -print0 | while IFS= read -r -d '' file; do
        # Break out of the loop if the maximum number of previews has been reached
        if [ "$max_previews" -ne 0 ] && [ "$count" -ge "$max_previews" ]; then
            break 2 # Break out of both the loop and the while read loop
        fi

        # Generate the output file path by replacing input_dir with output_dir and keeping the relative path
        output_file="${file/$input_dir/$output_dir}"
        output_file_dir="$(dirname "$output_file")"

        # Create the output directory if it doesn't exist
        mkdir -p "$output_file_dir"

        # Call the create_preview function
        create_preview "$file" "$output_file"
    done
done

echo "Previews generation completed."

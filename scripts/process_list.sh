#!/bin/bash

# Check if a file name is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file_with_list_of_filenames>"
    exit 1
fi

# Initialize a counter
counter=0

# Read the input file line by line
while IFS= read -r line; do
    # Display the file details using ls -l
    ls -l "$line"

    # Construct the new filename with a .MOV extension
    new_filename="${line%.*}.MOV"

    # Move the file to the new filename
    mv "$line" "$new_filename"

    # Increment the counter for each file processed
    ((counter++))
done < "$1"

# Print the number of files listed and moved
echo "Number of files processed: $counter"

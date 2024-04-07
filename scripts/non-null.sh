#!/bin/bash

# Check if the file path is provided as an argument
if [ $# -eq 0 ]; then
  echo "Please provide the file path as an argument."
  exit 1
fi

# Store the file path in a variable
file_path=$1

# Check if the file exists
if [ ! -f "$file_path" ]; then
  echo "File not found: $file_path"
  exit 1
fi

# Count the number of non-blank lines in the file
non_blank_lines=$(grep -c -v '^\s*$' "$file_path")

# Print the result
echo "Number of non-blank lines: $non_blank_lines"
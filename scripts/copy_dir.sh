#!/bin/bash

# Check if two arguments are given (source and destination)
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 source_directory destination_directory"
    exit 1
fi

# Assign the first and second arguments to variables
SOURCE_DIR=$1
DESTINATION_DIR=$2

# Copy the directory
cp -a "$SOURCE_DIR" "$DESTINATION_DIR"

# Check if the copy operation was successful
if [ $? -eq 0 ]; then
    echo "Directory copied successfully."
else
    echo "Error in copying directory."
    exit 1
fi

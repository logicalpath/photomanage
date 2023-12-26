#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <archive name>"
    exit 1
fi

# Assign the archive name to a variable
ARCHIVE_NAME="$1"

# Create a directory with the archive name
mkdir -p "$ARCHIVE_NAME"

# Unzip the archive into the directory
unzip -j "${ARCHIVE_NAME}" -d "${ARCHIVE_NAME%.zip}"

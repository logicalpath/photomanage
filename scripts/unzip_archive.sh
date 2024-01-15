#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <archive name with the .zip extenstion>"
    exit 1
fi

# Check if the arguement has a .zip extension
if [[ "$1" != *.zip ]]; then
    echo "Error: Argument must be a .zip file."
    exit 1
fi

# Check if the archive exists
if [ ! -f "$1" ]; then
    echo "Error: Archive $1 does not exist."
    exit 1
fi

# Assign the archive name to a variable without the .zip extension
ARCHIVE_NAME="${1%.zip}"

# Create a directory with the archive name
mkdir -p "$ARCHIVE_NAME"

# Unzip the archive into the directory
unzip -j "${ARCHIVE_NAME}" -d "${ARCHIVE_NAME%.zip}"

# Create a subdirectory called "json" in the directory
mkdir -p "${ARCHIVE_NAME}/json"

# if there are any .json files in the directory, move them to the json subdirectory
if ls "${ARCHIVE_NAME}"/*.json 1> /dev/null 2>&1; then
    mv "${ARCHIVE_NAME}"/*.json "${ARCHIVE_NAME}/json"
fi

# Create a subdirectory called "map" in the directory
mkdir -p "${ARCHIVE_NAME}/map"

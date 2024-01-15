#!/bin/bash

# Check if an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <Dir name>"
    exit 1
fi


# Check if the archive exists
if [ ! -d "$1" ]; then
    echo "Error: Dir $1 does not exist."
    exit 1
fi

# Assign the archive name to a variable
ARCHIVE_NAME="$1"


# Create a subdirectory called "json" in the directory
mkdir -p "${ARCHIVE_NAME}/json"

# if there are any .json files in the directory, move them to the json subdirectory
if ls "${ARCHIVE_NAME}"/*.json 1> /dev/null 2>&1; then
    mv "${ARCHIVE_NAME}"/*.json "${ARCHIVE_NAME}/json"
fi

# Create a subdirectory called "map" in the directory
mkdir -p "${ARCHIVE_NAME}/map"

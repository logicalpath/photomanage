#!/bin/bash

# Check if a file name was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 filename"
    exit 1
fi

# Read each line from the provided file
while IFS= read -r file
do
    sqlite-utils insert mediameta.db mappings "$file" --csv -d
done < "$1"

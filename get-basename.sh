#!/bin/bash

# Extract the folder name using parameter expansion
folder_name="${1##*/}"

# Handle the case when ~/ or a similar path is provided (no trailing folder)
if [[ -z "$folder_name" || "$folder_name" == ~ ]]; then
    folder_name="${1%/*}"
    folder_name="${folder_name##*/}"
fi

echo "$folder_name"

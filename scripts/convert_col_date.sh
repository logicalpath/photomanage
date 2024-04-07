#!/bin/bash

# Check if column name is provided as an argument
if [ $# -eq 0 ]; then
    echo "Please provide a column name as an argument."
    exit 1
fi

column_name=$1

# exif table
cat ../src/date_to_iso.py | sqlite-utils convert mediameta.db exif "$column_name" -


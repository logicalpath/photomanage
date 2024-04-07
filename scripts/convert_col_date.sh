#!/bin/bash

# exif table 
cat ../src/date_to_iso.py | sqlite-utils convert mediameta.db exif CreateDate - 

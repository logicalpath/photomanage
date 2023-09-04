#!/bin/bash


 

# This works where '.' is the current directory
# -r means recursive
exiftool -csv -"*GPS*" -"Date*" -r . > combined.csv


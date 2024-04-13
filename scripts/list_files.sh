#!/bin/bash

find . -type f ! -path '*/._*' -exec ls -l {} + > listfilenames.txt

find . -type f ! -path '*/._*' -exec ls -l {} + | awk '{print $5, $9}' > awkfilenames.txt

find . -type f ! -path '*/._*' -exec ls -l {} + | awk '{print $9, $5}' > awkpreview.txt
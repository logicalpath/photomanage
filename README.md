# photomanage
Scripts and ideas to manage tons and tons of images and movies


## Find media in apple photos library

``` find_media-photolibrary.sh folder```

This shell script searches for media files in directories with ".photoslibrary" in their name. It searches for media files within the "originals" subdirectory of each matching directory. The script defines a list of file extensions to search for, and uses this list to search for files with matching extensions. The script outputs the file paths of the matching files to a CSV file, along with their directory and file size. If a file does not match the desired extensions, its path is output to a separate exclusions file.

## Find media in a directory

``` find_media.sh folder```

This shell script searches for media files in a specified directory and its subdirectories. It extracts the folder name from the specified directory path, creates an output file, an exclusions file, and a JSON file with the folder name. It then defines a list of file extensions to search for, and uses this list to search for files with matching extensions in the specified directory and its subdirectories. The script outputs the file paths of the matching files to the output file, and any excluded files to the exclusions file.


## Sort the exclusions file

Find potential media types missed:

```cat exclusions.csv | awk -F '.' '{print $NF}' | sort | uniq```


## Get EXIF Data (Date & GPS)

For an apple photolibrary:
``` getExifData.py folder foldername```

For a regular folder with media:
``` getExifData.py photolib foldername```


Sort the output file by size:
`sort -t',' -k3 -n -r Movies-output.csv -o sorted_movies.csv`

### Download files with the CLI

`b2 authorize-account`

`b2 download-file-by-name b2-snapshots-xxxxxxxxx Aperture2016.zip ~/Downloads/Aperture2016.zip`

### Count files recursively excluding hidden files

` find . -type f ! -path '*/.*' | wc -l`

___

## Rename filenames to a uuid, move to a new directory and record this in a database

### Rename files in each directoey
`python src/rename-files.py <directory>`

### Move the files to a new directory
`scripts/move_uuid_dest.sh <source> <destination`

### From the original media root dir, get a list of mappings of old to new name 

`find . -name 'mapping.csv' > mappings.txt`

### Load the mappings into a sqlite db table
`./loadmap.sh mappings.txt`

### Get a list of the new filenames
Run from the root of the new filenames dir: `uuid`

`find . -type f ! -path '*/._*' > newfilenames.txt`

### parse the filennames into a csv file of Directory, File name
`python parse-newfiles.py newfilenames.txt filenames.csv`

### Load the filenames into a sqlite db table
`sqlite-utils insert mediameta.db filenames ./filenames.csv --csv -d`

## Get the exif data from the media files (script calls  exiftool)

```
√ database > ./getFoldersExif.sh ../uuid
./getFoldersExif.sh: line 3: Check: command not found
Searching ../uuid for media files...
The extracted folder name is: uuid
Exif file: uuid-exif.csv
Full Directory = ../uuid
exif_file = uuid-exif.csv
10452 image files read
10452 image files read
 7487 image files read
```

Note the total number of files read is 28,391


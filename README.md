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

Get list with filesize:
`find . -type f ! -path '*/._*' -exec ls -l {} + | awk '{print $9, $5}' > <filename>.txt`

### parse the filennames into a csv file of Directory, File name
`python parse-newfiles.py newfilenames.txt filenames.csv`

### Parse the awk file into csv
` python ./src/parse_awk.py ./awkthumb.txt`

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

### Load the exif data into a sqlite db table
`sqlite-utils insert mediameta.db exif ./uuid-exif.csv --csv -d`

### Convert dates
` cat ../src/date_to_iso.py| sqlite-utils convert mediameta.db exif CreateDate -`




---

Photos in datasette:

### Required Plugins

pipenv install datasette-media
pipenv install datasette-render-images

### Load the images

sqlite-utils insert-files media.db /Volumes/Eddie\ 4TB/MediaFiles/ThumbFiles/0/*.jpg

### bring up the media db

datasette -p 8002 --metadata metadata.json media.db

### extend time limit
`(photomanage) X1 database > datasette -p 8001 --setting sql_time_limit_ms 5500  --metadata metadata2.json mediameta.db`

### New config file 
`datasette -c datasette.yaml`


`datasette -p 8001 -c datasette.yaml mediameta.db`

`datasette -p 8001 --root --load-extension=spatialite  -c datasette.yaml mediameta.db`



### Being an actor - is this how to specify the actor on the command line?
`datasette --memory --actor '{"id": "root"}' --get '/-/actor.json'`

### Plugins

`datasette install datasette-write-ui`

`datasette install datasette-enrichments`

`datasette install datasette-enrichments-opencage`

`datasette install datasette-cluster-map`

`datasette install datasette-checkbox`


## Notes re gps:

In the exif file, rename GPSLatitude & GPSLongitude as latitude & longitude to avoid
calling open cage. Unless I change the plugin to use reverse gps to store address info

Or change the name of the columns in the datasette.yaml

```yaml
plugins:
  datasette-cluster-map:
    latitude_column: xlat
    longitude_column: xlng
```


## Display full images from disk

```yaml
plugins:

  datasette-media:
      photo:
        sql: "select prefixed_path as filepath from exif where FileName=:key"
```
The exif table contains a column called prefixed_path which contains the full path to the image. The FileName column contains the filename.

Then call the image like this:
```
http://127.0.0.1:8001/-/media/photo/<FileName>


http://127.0.0.1:8001/-/media/photo/04aa8750-9903-427c-bba6-8fb53512b6f2.jpg
```

And the image will be displayed.

Adding sqlite-vec for embeddings

For Datasette:
`datasette install datasette-sqlite-vec`

For sqlite-utils:
`sqlite-utils install sqlite-utils-sqlite-vec`


## Create duptime table

Find thumbnails where the CreateDate is within the same second.

`CREATE TABLE duptime AS SELECT thumbImages.content, exif.CreateDate, exif.FileName, thumbImages.size FROM exif INNER JOIN thumbImages ON exif.SourceFile = thumbImages.path WHERE exif.CreateDate IS NOT NULL AND exif.CreateDate <> '' AND exif.CreateDate IN (SELECT CreateDate FROM exif WHERE CreateDate IS NOT NULL AND exif.CreateDate <> '' GROUP BY CreateDate HAVING COUNT(*) > 1) ORDER BY exif.CreateDate;`







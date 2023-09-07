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
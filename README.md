# photomanage
Scripts and ideas to manage tons and tons of images and movies. The code was/is developted using ai coding agents. I started with chatgpt 4.0, then Claude with various models and now with Claude Code and Claude Sonnet 4.5 (as of Nov 23, 2025). 


## Find media in apple photos library

``` scripts/find_media_photolibrary.sh folder```

This shell script searches for media files in directories with ".photoslibrary" in their name. It searches for media files within the "originals" subdirectory of each matching directory. The script defines a list of file extensions to search for, and uses this list to search for files with matching extensions. The script outputs the file paths of the matching files to a CSV file, along with their directory and file size. If a file does not match the desired extensions, its path is output to a separate exclusions file.

## Find media in a directory

**Note:** `find_media.sh` script is not currently in the repository. Use `scripts/find_media_folders.sh` instead.

This shell script searches for media files in a specified directory and its subdirectories. It extracts the folder name from the specified directory path, creates an output file, an exclusions file, and a JSON file with the folder name. It then defines a list of file extensions to search for, and uses this list to search for files with matching extensions in the specified directory and its subdirectories. The script outputs the file paths of the matching files to the output file, and any excluded files to the exclusions file.


## Sort the exclusions file

Find potential media types missed:

```cat exclusions.csv | awk -F '.' '{print $NF}' | sort | uniq```


## Get EXIF Data (Date & GPS)

**Note:** `getExifData.py` script is not currently in the repository. Use `scripts/getFoldersExif.sh` or `scripts/getAllExif.sh` instead.


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
`scripts/loadmap.sh mappings.txt`

### Get a list of the new filenames
Run from the root of the new filenames dir: `uuid`

`find . -type f ! -path '*/._*' > newfilenames.txt`

Get list with filesize:
`find . -type f ! -path '*/._*' -exec ls -l {} + | awk '{print $9, $5}' > <filename>.txt`

### parse the filennames into a csv file of Directory, File name
`python src/parse-newfiles.py newfilenames.txt filenames.csv`

### Parse the awk file into csv
` python ./src/parse_awk.py ./awkthumb.txt`

### Load the filenames into a sqlite db table
`sqlite-utils insert mediameta.db filenames ./filenames.csv --csv -d`

## Get the exif data from the media files (script calls  exiftool)

```
√ database > scripts/getFoldersExif.sh ../uuid
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

### Extract image dimensions

First, add ImageWidth and ImageHeight columns to the exif table:
```bash
sqlite3 mediameta.db "ALTER TABLE exif ADD COLUMN ImageWidth INTEGER;"
sqlite3 mediameta.db "ALTER TABLE exif ADD COLUMN ImageHeight INTEGER;"
```

Extract dimensions using exiftool:
```bash
cd database
../scripts/getImageDimensions.sh "/Volumes/Eddie 4TB/MediaFiles/uuid"
```

Import the dimension data into the database:
```bash
python ../scripts/update_image_dimensions.py image-dimensions.csv mediameta.db
```

---

Photos in datasette:

### Required Plugins

uv add datasette-media
uv add datasette-render-images

### Load the images

sqlite-utils insert-files media.db /Volumes/Eddie\ 4TB/MediaFiles/ThumbFiles/0/*.jpg

### Generate and load thumbnails (Modern approach - November 2025)

**Generate auto-oriented 512x512 thumbnails:**
```bash
scripts/create_thumbs_oriented.sh /Volumes/Eddie\ 4TB/MediaFiles/uuid database/512x512 512x512>
```

This creates thumbnails with:
- Auto-orientation based on EXIF data (fixes sideways images)
- 512x512 max dimensions (prevents upsampling with `>` flag)
- Preserved original file extensions

**Load thumbnails into database:**
```bash
python3 scripts/load_thumbnails_to_db.py
```

This script:
- Clears existing thumbnails from `thumbImages` table
- Loads all files from `database/512x512/` directory
- Transforms paths from `database/512x512/0/file.jpg` to `./0/file.jpg`
- Inserts BLOB content, file size, and path

**Populate CreateDate column:**
After loading thumbnails, populate the `CreateDate` column from the `exif` table:
```bash
sqlite3 database/mediameta.db "UPDATE thumbImages SET CreateDate = (SELECT CreateDate FROM exif WHERE exif.SourceFile = thumbImages.path)"
```

This links thumbnails to their EXIF metadata creation dates.

### Start Datasette

From the `database/` directory:

```bash
cd database
datasette -p 8001 --root --load-extension=spatialite \
    --template-dir ../datasette/templates \
    -c ../datasette/datasette.yaml \
    mediameta.db
```

**Note:** Templates are in `datasette/templates/`, not `database/templates/`.

### Plugins

`datasette install datasette-cluster-map`

`datasette install datasette-checkbox`

**Note:** The following plugins are not currently installed:
- `datasette-write-ui`
- `datasette-enrichments`
- `datasette-enrichments-opencage`


## Notes re GPS and Maps

**Important:** The `datasette-enrichments-opencage` plugin (if installed) automatically looks for columns named `GPSLatitude` and `GPSLongitude` to perform reverse geocoding.

**Current Configuration:**
- `datasette-cluster-map` is configured to use `GPSLatitude` and `GPSLongitude` columns
- `datasette-enrichments-opencage` is NOT currently installed (config removed from datasette.yaml)
- The `exif` table has ~33K photos with GPS data

**Options to avoid unintended opencage API calls (if plugin were installed):**

1. Rename columns in the exif table from `GPSLatitude` & `GPSLongitude` to `latitude` & `longitude`
2. Keep current column names but configure datasette-cluster-map to use different column names:
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
        sql: "select full_path as filepath from exif_with_fullpath where FileName=:key"
```

The system uses a database-native configuration approach:
- **Configuration Table**: `photomanage_config` stores the media prefix path
- **Dynamic View**: `exif_with_fullpath` computes full paths on-demand
- **Source Data**: `exif` table contains only source data (no computed paths)

### Managing the Media Prefix Path

The media file location prefix is stored in the `photomanage_config` database table. When media files are moved to a new location, simply update the configuration:

```sql
UPDATE photomanage_config
SET value = '/new/path/to/media'
WHERE key = 'media_prefix_path';
```

The `exif_with_fullpath` view will automatically use the new prefix - no migration script needed!

#### View the Current Configuration

```sql
SELECT * FROM photomanage_config;
```

#### How It Works

The `exif_with_fullpath` view dynamically computes full paths by combining:
- The prefix from `photomanage_config` table
- The relative path from `exif.SourceFile`

Example:
```
SourceFile:  ./0/example.jpg
Config:      /Volumes/Eddie 4TB/MediaFiles/uuid
Result:      /Volumes/Eddie 4TB/MediaFiles/uuid/0/example.jpg
```

**Benefits:**
- Paths always accurate (never stale)
- No maintenance scripts needed
- Simple configuration updates
- SQL-accessible configuration


#### Viewing Images

**Photo Gallery (Thumbnail Carousel)**

Browse photos with a responsive thumbnail grid at:
```
http://127.0.0.1:8001/gallery
```

Features:
- Filter by date range (start date and/or end date)
- Click thumbnails to view full photo with metadata
- Pagination (100 photos per page with Previous/Next navigation)
- Auto-oriented 512x512 thumbnails for optimal quality
- Responsive grid layout

Example with date filter:
```
http://127.0.0.1:8001/gallery?start_date=2016-01-01&end_date=2016-12-31
```

**Individual Photo Page**

View a single photo with full metadata at:
```
http://127.0.0.1:8001/photo/<FileName>
```

Example:
```
http://127.0.0.1:8001/photo/00126662-8f53-4042-a3e0-a291170a004e.jpg
```

**Direct Media Access**

Access images using the datasette-media plugin URL format:
```
http://127.0.0.1:8001/-/media/photo/<FileName>
```

Example:
```
http://127.0.0.1:8001/-/media/photo/00126662-8f53-4042-a3e0-a291170a004e.jpg
```

**What happens:**
1. You access: `http://127.0.0.1:8001/-/media/photo/00126662-8f53-4042-a3e0-a291170a004e.jpg`
2. The `photo` part matches the config key in `datasette.yaml`
3. The filename `00126662-8f53-4042-a3e0-a291170a004e.jpg` becomes the `:key` parameter
4. Datasette runs:
   ```sql
   SELECT full_path as filepath
   FROM exif_with_fullpath
   WHERE FileName='00126662-8f53-4042-a3e0-a291170a004e.jpg'
   ```
5. Returns the full path, and datasette-media serves the image

## Database Optimization

### Creating Performance Indexes

The database uses indexes on frequently queried columns for optimal performance:

```bash
python src/create_indexes.py
```

This creates indexes on:
- `exif.FileName` - For photo lookups (100-1000x faster)
- `thumbImages.path` - For JOIN operations
- `exif.CreateDate` - For date-based queries
- `ai_description.file` - For AI description JOINs

**Performance impact**: Photo lookups improve from O(n) full table scans to O(log n) index seeks.

See [docs/database-indexes.md](docs/database-indexes.md) for detailed analysis and recommendations.

### Database Architecture

See documentation for system architecture details:
- [docs/config-table-migration.md](docs/config-table-migration.md) - Configuration management
- [docs/sourcefile-consistency-analysis.md](docs/sourcefile-consistency-analysis.md) - Path architecture
- [docs/database-indexes.md](docs/database-indexes.md) - Index optimization

## Extensions and Embeddings

Adding sqlite-vec for embeddings

For Datasette:
`datasette install datasette-sqlite-vec`

For sqlite-utils:
`sqlite-utils install sqlite-utils-sqlite-vec`


## Create duptime table

Find thumbnails where the CreateDate is within the same second.

`CREATE TABLE duptime AS SELECT thumbImages.content, exif.CreateDate, exif.FileName, thumbImages.size FROM exif INNER JOIN thumbImages ON exif.SourceFile = thumbImages.path WHERE exif.CreateDate IS NOT NULL AND exif.CreateDate <> '' AND exif.CreateDate IN (SELECT CreateDate FROM exif WHERE CreateDate IS NOT NULL AND exif.CreateDate <> '' GROUP BY CreateDate HAVING COUNT(*) > 1) ORDER BY exif.CreateDate;`

## Troubleshooting

### Set Pipenv to Use Pyenv Python

```bash
export PIPENV_PYTHON="$HOME/.pyenv/shims/python"

# Make it permanent
echo 'export PIPENV_PYTHON="$HOME/.pyenv/shims/python"' >> ~/.zshrc
```

### Check Python Compilation Flags

```bash
python -c "import sysconfig; print(sysconfig.get_config_var('CONFIG_ARGS'))"
```

### Rebuild Python with SQLite Extensions Support

```bash
PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" \
LDFLAGS="-L/opt/homebrew/opt/sqlite/lib" \
CPPFLAGS="-I/opt/homebrew/opt/sqlite/include" \
pyenv install 3.12.5 --force
```

**Verify the fix:**

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
python -c "import sqlite3; print(sqlite3.connect(':memory:').enable_load_extension(True))"
```

**Recreate uv environment:**

```bash
rm -rf .venv
uv venv --python 3.12.5
uv sync --no-install-project
source .venv/bin/activate
```

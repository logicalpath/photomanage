# photomanage

Photomanage is a repo for managing personal photos. Currently, this is for managing a static set of photos and videos. There are about 33,000 files totaling 141 Gigabytes. The database maps exif data to all the files. A table of thumbprints exists for about 31,800 files (only 15 images failed to produce thumbprints). There are about 1,100 video files.

The full image files and video files live in an external drive.


## First-time Setup

### System dependencies

`pyheif` requires `libheif`. Install it with Homebrew before running `uv sync`:

```bash
brew install libheif
```

Datasette uses the SpatiaLite SQLite extension. Install it:

```bash
brew install spatialite-tools
```

### Create the Python environment

```bash
uv sync
```

This creates a `.venv` and installs all dependencies.

**If you need to rebuild from scratch** (e.g. environment is broken):

```bash
rm -rf .venv
uv sync
```

### Environment variables

No environment variables are required for a standard setup. Two optional variables let you override default database paths:

| Variable | Default | Purpose |
|---|---|---|
| `MEDIAMETA_DB_PATH` | `database/mediameta.db` | Path to media metadata database |
| `EMBEDDINGS_DB_PATH` | `database/embeddings-vlm2.db` | Path to embeddings database |

These are not loaded automatically — export them in your shell before running datasette:

```bash
export MEDIAMETA_DB_PATH=/custom/path/mediameta.db
export EMBEDDINGS_DB_PATH=/custom/path/embeddings-vlm2.db
```

### SQLite with loadable extensions (if needed)

If `--load-extension=spatialite` fails, Python may have been compiled without loadable extension support. Rebuild it:

```bash
PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" \
LDFLAGS="-L/opt/homebrew/opt/sqlite/lib" \
CPPFLAGS="-I/opt/homebrew/opt/sqlite/include" \
pyenv install 3.12.5 --force
```

Verify:

```bash
python -c "import sqlite3; print(sqlite3.connect(':memory:').enable_load_extension(True))"
```

Then recreate the uv environment:

```bash
rm -rf .venv
uv sync
```


## Start Datasette

From the `database/` directory:

```bash
cd database
uv run datasette -p 8001 --host 0.0.0.0 --load-extension=spatialite --template-dir ../datasette/templates --plugins-dir=../datasette/plugins -c ../datasette/datasette.yaml mediameta.db embeddings-vlm2.db
```

`--host 0.0.0.0` binds to all network interfaces so datasette is reachable by hostname or IP from other machines on the network (e.g. `http://eddies-mac-studio.local:8001`). This exposes the instance — including all media and metadata — to anyone on the LAN. Omit `--host 0.0.0.0` to restrict access to localhost only.

Templates are in `datasette/templates/` and plugins are in `datasette/plugins/`.


## Viewing Images

**Photo Gallery (Thumbnail Carousel)**

Browse photos with a responsive thumbnail grid at:
```
http://<hostname>:8001/gallery
```

Features:
- Semantic search — type a natural-language query (e.g., "kids playing soccer") to find photos by meaning
- Filter by date range (start date and/or end date)
- Click thumbnails to view full photo with metadata
- Pagination (100 photos per page with Previous/Next navigation)
- Auto-oriented 512x512 thumbnails for optimal quality
- Responsive grid layout

Example with date filter:
```
http://<hostname>:8001/gallery?start_date=2016-01-01&end_date=2016-12-31
```

**Individual Photo Page**

View a single photo with full metadata at:
```
http://<hostname>:8001/photo/<FileName>
```

**Direct Media Access**

```
http://<hostname>:8001/-/media/photo/<FileName>
```

What happens:
1. The `photo` part matches the config key in `datasette.yaml`
2. The filename becomes the `:key` parameter
3. Datasette runs a SQL query against `exif_with_fullpath`
4. `datasette-media` serves the image from disk


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

The `exif_with_fullpath` view will automatically use the new prefix — no migration needed.

View the current configuration:

```sql
SELECT * FROM photomanage_config;
```

Example path resolution:
```
SourceFile:  ./0/example.jpg
Config:      /Volumes/Eddie 4TB/MediaFiles/uuid
Result:      /Volumes/Eddie 4TB/MediaFiles/uuid/0/example.jpg
```


## Plugins

### Required

```bash
uv add datasette-checkbox
uv add datasette-media
uv add datasette-render-images
```

### Optional

```bash
datasette install datasette-cluster-map
```

Not currently installed:
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


## Database Optimization

### Creating Performance Indexes

```bash
python src/create_indexes.py
```

This creates indexes on:
- `exif.FileName` - For photo lookups (100-1000x faster)
- `thumbImages.path` - For JOIN operations
- `exif.CreateDate` - For date-based queries
- `image_description.file` - For image description JOINs

See [docs/database-indexes.md](docs/database-indexes.md) for detailed analysis.

### Database Architecture

- [docs/config-table-migration.md](docs/config-table-migration.md) - Configuration management
- [docs/sourcefile-consistency-analysis.md](docs/sourcefile-consistency-analysis.md) - Path architecture
- [docs/database-indexes.md](docs/database-indexes.md) - Index optimization


## AI Image Descriptions

Generate natural-language descriptions of photos using SmolVLM2 on Apple Silicon. Descriptions are stored in the `image_description` table in `database/mediameta.db`.

See [docs/mlx-vlm-usage.md](docs/mlx-vlm-usage.md) for installation, usage, and batch processing details.


## Semantic Search (Embeddings)

Search your photo collection by meaning using embeddings generated from the AI descriptions. Uses Simon Willison's `llm` tool with local sentence-transformer models.

See [docs/embedding-search.md](docs/embedding-search.md) for the full runbook.


## Troubleshooting

### Check Python Compilation Flags

```bash
python -c "import sysconfig; print(sysconfig.get_config_var('CONFIG_ARGS'))"
```

### Yanked numpy warning

`uv` may warn that `numpy==2.4.0` is yanked. This is a known upstream issue and does not affect functionality.


---

## Data Ingestion (reference)

The sections below document the one-time data ingestion pipeline. They are reference material for understanding how the database was built.

### Generate and load thumbnails

**Generate auto-oriented 512x512 thumbnails:**
```bash
scripts/create_thumbs_oriented.sh /Volumes/Eddie\ 4TB/MediaFiles/uuid database/512x512 512x512
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
```bash
sqlite3 database/mediameta.db "UPDATE thumbImages SET CreateDate = (SELECT CreateDate FROM exif WHERE exif.SourceFile = thumbImages.path)"
```

### Get EXIF Data

**Note:** Use `scripts/getFoldersExif.sh` or `scripts/getAllExif.sh`.

```bash
scripts/getFoldersExif.sh ../uuid
```

Load exif data into the database:
```bash
sqlite-utils insert mediameta.db exif ./uuid-exif.csv --csv -d
```

Convert dates:
```bash
cat ../src/date_to_iso.py | sqlite-utils convert mediameta.db exif CreateDate -
```

### Extract image dimensions

```bash
sqlite3 mediameta.db "ALTER TABLE exif ADD COLUMN ImageWidth INTEGER;"
sqlite3 mediameta.db "ALTER TABLE exif ADD COLUMN ImageHeight INTEGER;"
cd database
../scripts/getImageDimensions.sh "/Volumes/Eddie 4TB/MediaFiles/uuid"
python ../scripts/update_image_dimensions.py image-dimensions.csv mediameta.db
```

### Rename files to UUID and load into database

```bash
python src/rename-files.py <directory>
scripts/move_uuid_dest.sh <source> <destination>
find . -name 'mapping.csv' > mappings.txt
scripts/loadmap.sh mappings.txt
find . -type f ! -path '*/._*' > newfilenames.txt
python src/parse-newfiles.py newfilenames.txt filenames.csv
sqlite-utils insert mediameta.db filenames ./filenames.csv --csv -d
```

### Download files with B2 CLI

```bash
b2 authorize-account
b2 download-file-by-name b2-snapshots-xxxxxxxxx Aperture2016.zip ~/Downloads/Aperture2016.zip
```

### Create duptime table

Find thumbnails where the CreateDate is within the same second:

```sql
CREATE TABLE duptime AS
SELECT thumbImages.content, exif.CreateDate, exif.FileName, thumbImages.size
FROM exif
INNER JOIN thumbImages ON exif.SourceFile = thumbImages.path
WHERE exif.CreateDate IS NOT NULL
  AND exif.CreateDate <> ''
  AND exif.CreateDate IN (
    SELECT CreateDate FROM exif
    WHERE CreateDate IS NOT NULL AND exif.CreateDate <> ''
    GROUP BY CreateDate HAVING COUNT(*) > 1
  )
ORDER BY exif.CreateDate;
```


---

## Find media (reference)

### Find media in Apple Photos library

```bash
scripts/find_media_photolibrary.sh <folder>
```

Searches directories with `.photoslibrary` in their name, looking inside the `originals` subdirectory. Outputs matching file paths to a CSV file and excluded files to a separate exclusions file.

### Find media in a directory

**Note:** Use `scripts/find_media_folders.sh`.

Searches a specified directory recursively for media files, outputting matches to a CSV and exclusions to a separate file.

### Sort the exclusions file

Find potential media types missed:

```bash
cat exclusions.csv | awk -F '.' '{print $NF}' | sort | uniq
```

### Sort output by size

```bash
sort -t',' -k3 -n -r Movies-output.csv -o sorted_movies.csv
```

### Count files recursively (excluding hidden files)

```bash
find . -type f ! -path '*/.*' | wc -l
```

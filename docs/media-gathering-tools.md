# Media Gathering Tools and Workflows

## Overview
This document provides a comprehensive analysis of all tools, scripts, and commands used for discovering, listing, and gathering media files in the photomanage project.

---

## Table of Contents
1. [README Commands: Automated vs Manual](#readme-commands-automated-vs-manual)
2. [Primary Media Discovery Tools](#primary-media-discovery-tools)
3. [EXIF Metadata Extraction](#exif-metadata-extraction)
4. [File Listing Utilities](#file-listing-utilities)
5. [Thumbnail Generation](#thumbnail-generation)
6. [Video Preview Generation](#video-preview-generation)
7. [Python File Discovery Scripts](#python-file-discovery-scripts)
8. [Supported File Formats](#supported-file-formats)
9. [Common Workflows](#common-workflows)
10. [Dependencies](#dependencies)

---

## README Commands: Automated vs Manual

The README.md file documents 9 distinct command patterns. This section categorizes each command as either **automated** (implemented in scripts/src files) or **manual** (one-off workflow commands).

### ✅ Automated Commands (Implemented in Scripts)

These commands have corresponding implementations in the scripts/ or src/ directories:

| # | README Command | Implementation | File Location | Notes |
|---|----------------|----------------|---------------|-------|
| 1 | `scripts/find_media_photolibrary.sh folder` | Standalone Script | `scripts/find_media_photolibrary.sh` | Direct match |
| 2 | `find_media.sh` (deprecated) | Alternative Script | `scripts/find_media_folders.sh` | Replacement for missing script |
| 3 | `getExifData.py` (deprecated) | Alternative Scripts | `scripts/getFoldersExif.sh`<br>`scripts/getAllExif.sh` | Shell alternatives for missing Python script |
| 4 | `find . -type f ! -path '*/.*' \| wc -l` | Within Script | `scripts/move_uuid_dest.sh:26,44` | Used for file count verification |
| 5 | `find . -type f ! -path '*/._*' -exec ls -l {} + \| awk '{print $9, $5}'` | Standalone Script | `scripts/list_files.sh:5,7` | Multiple output variations |
| 6 | `b2 authorize-account`<br>`b2 download-file-by-name` | Python SDK Wrapper | `src/b2-file.py` | Uses `b2sdk.v2` instead of CLI commands |

**Total: 6 command patterns with implementations**

---

### ⚠️ Manual Workflow Commands (No Automation)

These commands are one-off data manipulation tasks shown as examples in the README. They are not automated within any scripts:

| # | README Command | Purpose | Why Manual |
|---|----------------|---------|------------|
| 1 | `cat exclusions.csv \| awk -F '.' '{print $NF}' \| sort \| uniq` | Find potential media types missed in discovery | Ad-hoc data analysis to discover new extensions |
| 2 | `sort -t',' -k3 -n -r Movies-output.csv -o sorted_movies.csv` | Sort media files by size | One-time CSV sorting for exploration |
| 3 | `find . -name 'mapping.csv' > mappings.txt` | Locate all mapping CSVs from rename operations | One-time file discovery for workflow setup |

**Total: 3 command patterns as manual examples only**

---

### Key Insights

- **66% automated** (6 of 9 commands have script implementations)
- **33% manual-only** (3 of 9 are ad-hoc workflow commands)
- **All primary operations are automated:** Media finding, EXIF extraction, file listing, cloud integration
- **Manual commands are for:** Extension discovery, CSV sorting, mapping file location
- **Implementation approaches:**
  - **Direct scripts:** find_media_photolibrary.sh, find_media_folders.sh
  - **Alternative implementations:** getFoldersExif.sh replaces getExifData.py
  - **Embedded in scripts:** File counting in move_uuid_dest.sh
  - **Different technology:** Python SDK instead of B2 CLI

---

## Primary Media Discovery Tools

### find_media_folders.sh (RECOMMENDED)
**Location:** `scripts/find_media_folders.sh`

**Purpose:** General-purpose media file discovery in any directory structure

**Usage:**
```bash
scripts/find_media_folders.sh <directory>
```

**Input:** Top-level directory path

**Output:**
- `{folder}-output.csv` - Directory, File, FileSize
- `{folder}-exclusions.csv` - Non-matching files
- `{folder}-json.txt` - JSON files found

**File formats:** jpeg, jpg, nef, png, mov, mp4, 3g2, 3gp, aae, avi, gif, heic, m4v, mpg, pdf, psd, tiff, tif

**Key features:**
- Recursive search of entire directory tree
- Three-way classification: media files, JSON files, exclusions
- Case-insensitive extension matching
- Cleans up old output files before starting

**Dependencies:** `find`, `grep`, `stat`, `get-basename.sh`

**Status:** ✅ Active, replaces deprecated `find_media.sh`

---

### find_media_photolibrary.sh
**Location:** `scripts/find_media_photolibrary.sh`

**Purpose:** Find media in Apple Photos library bundles

**Usage:**
```bash
scripts/find_media_photolibrary.sh <folder>
```

**Input:** Top-level directory containing `.photoslibrary` folders

**Output:**
- `{folder}-output.csv` - Directory, File, FileSize
- `{folder}-exclusions.csv` - Non-matching files

**File formats:** jpeg, jpg, nef, png, mov, mp4, 3g2, 3gp, aae, avi, gif, heic, m4v, mpg, pdf, psd, tiff

**Key features:**
- Searches for directories with `.photoslibrary` in name
- Looks specifically in `originals` subdirectory
- Uses macOS `stat -f %z` for file sizes

**Dependencies:** `find`, `grep`, `stat`, `get-basename.sh`

**Status:** ✅ Active, specialized for Apple Photos

---

### find_media_fcpbundle.sh
**Location:** `scripts/find_media_fcpbundle.sh`

**Purpose:** Find media in Final Cut Pro bundle directories

**Usage:**
```bash
scripts/find_media_fcpbundle.sh <directory>
```

**Input:** Top-level directory containing `.fcpbundle` directories

**Output:**
- `{folder}-output.csv` - Directory, File, FileSize
- `{folder}-exclusions.csv` - Non-matching files

**File formats:** jpeg, jpg, nef, png, mov, mp4, 3g2, 3gp, aae, avi, gif, heic, m4v, mpg, pdf, psd, tiff

**Key features:**
- Finds `.fcpbundle` directories specifically
- Uses `find -depth` for deep directory traversal
- Targeted at video editing project archives

**Dependencies:** `find`, `grep`, `stat`, `get-basename.sh`

**Status:** ✅ Active, specialized use case

---

### file_extensions.sh
**Location:** `scripts/file_extensions.sh`

**Purpose:** Discover all unique file extensions in a directory tree

**Usage:**
```bash
cd <directory>
../scripts/file_extensions.sh
```

**Output:** `file_extensions.txt` with sorted unique extensions

**Key features:**
- Uses `sed` to extract extensions after last dot
- Sorts and deduplicates
- Useful for discovering new media types to add to scripts

**Dependencies:** `find`, `sed`, `sort`, `uniq`

**Status:** ✅ Active utility

---

## EXIF Metadata Extraction

### getFoldersExif.sh (RECOMMENDED)
**Location:** `scripts/getFoldersExif.sh`

**Purpose:** Extract comprehensive EXIF date and GPS data from media files

**Usage:**
```bash
scripts/getFoldersExif.sh <directory>
```

**Output:** `{folder}/exif.csv` with extensive date/GPS fields

**Fields extracted:**
- CreateDate, DateCreated, ProfileDateTime, DateTimeOriginal
- ModifyDate, PreviewDate
- GPSDateStamp, GPSDateTime
- GPSLatitude, GPSLongitude (numeric)
- FileName (without path)

**File formats:** All formats supported by exiftool (excludes `._*` files)

**Key features:**
- Extensive date field extraction
- Numeric GPS coordinates
- Output saved to subfolder within target directory
- Documented in README as recommended approach

**Dependencies:** `find`, `exiftool`, `get-basename.sh`

**Status:** ✅ Active, recommended in README

**README example:**
```bash
scripts/getFoldersExif.sh ../uuid
```

---

### getAllExif.sh (RECOMMENDED)
**Location:** `scripts/getAllExif.sh`

**Purpose:** Extract ALL time and GPS metadata fields from media files

**Usage:**
```bash
scripts/getAllExif.sh <directory>
```

**Output:** `{folder}/exifAll.csv` with all time/GPS tags

**File formats:** All exiftool-supported formats (excludes `._*`)

**Key features:**
- Uses `exiftool -time:all -gps:all` for comprehensive extraction
- Group names included (`-G1`)
- All values shown even if duplicate (`-a`)
- Short tag names (`-s`)
- Most comprehensive metadata extraction available

**Dependencies:** `find`, `exiftool`, `get-basename.sh`

**Status:** ✅ Active, recommended in README

---

### getMoreExif.sh
**Location:** `scripts/getMoreExif.sh`

**Purpose:** Extract image dimensions, megapixels, and all time/GPS data

**Usage:**
```bash
scripts/getMoreExif.sh <directory>
```

**Output:** `{folder}/exifMore.csv`

**Fields extracted:**
- ImageSize
- Megapixels
- All time tags
- All GPS tags

**Dependencies:** `find`, `exiftool`, `get-basename.sh`

**Status:** ✅ Active

---

### getImageDimensions.sh
**Location:** `scripts/getImageDimensions.sh`

**Purpose:** Extract only width and height dimensions from images

**Usage:**
```bash
scripts/getImageDimensions.sh <directory>
```

**Output:** `image-dimensions.csv` with FileName, ImageWidth, ImageHeight

**Key features:**
- Focused extraction (dimensions only)
- Numeric values only (`-n` flag)
- Validates directory exists
- Checks for exiftool installation
- Used with `update_image_dimensions.py` to update database

**Dependencies:** `find`, `exiftool`

**Status:** ✅ Active, part of documented workflow

**README example:**
```bash
cd database
../scripts/getImageDimensions.sh "/Volumes/Eddie 4TB/MediaFiles/uuid"
```

---

### getExifData.sh (Deprecated)
**Location:** `scripts/getExifData.sh`

**Purpose:** Multi-mode EXIF extraction (folder/photolib/fcpbundle)

**Status:** ⚠️ Active but README recommends using `getFoldersExif.sh` or `getAllExif.sh` instead

**Note from README:**
> **Note:** `getExifData.py` script is not currently in the repository. Use `scripts/getFoldersExif.sh` or `scripts/getAllExif.sh` instead.

---

## File Listing Utilities

This section covers both automated scripts and manual README commands for file listing operations.

### 🤖 Automated: list_files.sh
**Location:** `scripts/list_files.sh`

**Purpose:** Generate multiple file listing formats for database workflows

**Usage:**
```bash
cd <directory>
../scripts/list_files.sh
```

**Output:**
- `listfilenames.txt` - Full `ls -l` output
- `awkfilenames.txt` - Filesize, filename (space-separated)
- `awkpreview.txt` - Filename, filesize (space-separated)

**File formats:** All files (not filtered by type)

**Key features:**
- Excludes Apple resource fork files (`._*`)
- Three different output formats for flexibility
- Uses `awk` for structured data extraction
- **Implements README pattern:** `find . -type f ! -path '*/._*' -exec ls -l {} + | awk '{print $9, $5}'`

**Dependencies:** `find`, `ls`, `awk`

**Status:** ✅ Active

---

### 🤖 Automated: File Counting (Embedded)
**Location:** `scripts/move_uuid_dest.sh:26,44`

**Purpose:** Count all non-hidden files in directory tree

**Command:**
```bash
find . -type f ! -path '*/.*' | wc -l
```

**Usage:** Automatically used within move_uuid_dest.sh for verification

**Key features:**
- Counts files before and after move operation
- Validates file transfer completeness
- **Implements README pattern exactly**

**Status:** ✅ Active (embedded in script)

---

### 📝 Manual: README File Listing Commands

These commands appear in the README as manual workflow examples:

#### Get list of new filenames (MANUAL)
```bash
# Simple list
find . -type f ! -path '*/._*' > newfilenames.txt

# With file sizes (filename, size)
find . -type f ! -path '*/._*' -exec ls -l {} + | awk '{print $9, $5}' > <filename>.txt

# With file sizes (size, filename)
find . -type f ! -path '*/._*' -exec ls -l {} + | awk '{print $5, $9}' > <filename>.txt
```
**Purpose:** Generate file listings for database import workflows

**Implementation Status:** ⚠️ Partially automated - list_files.sh implements the awk pattern variants

**Status:** ✅ Active (part of rename/move workflow)

---

#### Find mapping files (MANUAL)
```bash
find . -name 'mapping.csv' > mappings.txt
```
**Purpose:** Locate all mapping CSVs from rename operations

**Implementation Status:** ❌ No automation - manual one-off command

**Status:** ✅ Active (part of UUID rename workflow)

---

#### Sort exclusions to find missed media types (MANUAL)
```bash
cat exclusions.csv | awk -F '.' '{print $NF}' | sort | uniq
```
**Purpose:** Analyze excluded files to discover media types not in extension list

**Implementation Status:** ❌ No automation - manual data analysis command

**Status:** ✅ Active utility workflow

---

### remove_apple_double.sh
**Location:** `scripts/remove_apple_double.sh`

**Purpose:** Find or remove macOS resource fork files (`._*`)

**Usage:**
```bash
# Display mode (safe preview)
scripts/remove_apple_double.sh -d

# Remove mode (destructive)
scripts/remove_apple_double.sh -x

# Specify directory
scripts/remove_apple_double.sh -d -i /path/to/directory
```

**Key features:**
- Safe preview mode (`-d`)
- Destructive mode (`-x`)
- Customizable search directory
- Cleans up AppleDouble artifacts

**Dependencies:** `find`, `rm`

**Status:** ✅ Active utility

---

## Thumbnail Generation

### create_thumbs_oriented.sh (RECOMMENDED - November 2025)
**Location:** `scripts/create_thumbs_oriented.sh`

**Purpose:** Generate auto-oriented thumbnails with proper EXIF rotation handling

**Usage:**
```bash
scripts/create_thumbs_oriented.sh <input_dir> <output_dir> [resize] [max_count] [error_log]
```

**Parameters:**
- `input_directory` - Source directory with original images
- `output_directory` - Where thumbnails will be saved
- `resize_dimensions` - Optional, default: `512x512>` (no upsampling)
- `max_thumbnails` - Optional, default: 0 (unlimited)
- `error_log` - Optional, default: `error_log.txt`

**Output:**
- Thumbnail images preserving directory structure
- Error log file

**File formats:**
- Standard: heic, jpg, png, aae, jpeg, tif, tiff
- RAW: nef, arw (using dcraw extraction)

**Key features:**
- **Auto-orientation**: Uses `-auto-orient` flag to fix sideways images
- **No upsampling**: `>` flag prevents enlarging small images
- Preserves original file extensions
- Preserves directory structure from input
- Separate handling for RAW formats (dcraw)
- Recursive directory processing
- Skips output directory in traversal

**Dependencies:** ImageMagick (`magick`), `dcraw` (for RAW), `file`

**Status:** ✅ Active, modern approach documented in README

**README example:**
```bash
scripts/create_thumbs_oriented.sh /Volumes/Eddie\ 4TB/MediaFiles/uuid database/512x512 512x512>
```

**README notes:**
> This creates thumbnails with:
> - Auto-orientation based on EXIF data (fixes sideways images)
> - 512x512 max dimensions (prevents upsampling with `>` flag)
> - Preserved original file extensions

---

### create_thumbnails.sh
**Location:** `scripts/create_thumbnails.sh`

**Purpose:** Basic thumbnail creation using ImageMagick

**Usage:**
```bash
scripts/create_thumbnails.sh <input_dir> <output_dir> [resize] [max_count] [error_log]
```

**File formats:** heic, jpg, nef, png, aae, jpeg, tif, tiff

**Key features:**
- Uses `find` for file discovery
- Simpler than oriented version (no auto-orient)
- Flattened output (no directory structure preservation)

**Dependencies:** `find`, ImageMagick (`magick`)

**Status:** ✅ Active, older approach

---

### create_thumbsNEF.sh
**Location:** `scripts/create_thumbsNEF.sh`

**Purpose:** Create thumbnails with special RAW format handling

**File formats:**
- Standard: heic, jpg, png, aae, jpeg, tif, tiff
- RAW: nef, arw (using dcraw)

**Key features:**
- Separate code paths for RAW vs standard formats
- Preserves directory structure
- RAW files keep original extension, others convert to .jpg

**Dependencies:** `dcraw`, ImageMagick (`magick`), `file`

**Status:** ✅ Active, predecessor to create_thumbs_oriented.sh

---

## Video Preview Generation

### create_preview.sh
**Location:** `scripts/create_preview.sh`

**Purpose:** Create short video preview clips using ffmpeg

**Usage:**
```bash
scripts/create_preview.sh <input_dir> <output_dir> [max_previews]
```

**Output:** 10-second preview videos starting at 5 seconds into original

**File formats:** mp4, mov, avi, mpg, 3gp, m4v

**Key features:**
- Extracts 10 seconds starting at 5-second mark
- Scales to 320px width
- Uses fast encoding preset
- Preserves relative directory structure

**Dependencies:** `ffmpeg`, `find`

**Status:** ✅ Active

---

### preview_creator.py
**Location:** `src/preview_creator.py`

**Purpose:** Python version of video preview creation

**Usage:**
```bash
python src/preview_creator.py <input_dir> <output_dir> [max_previews]
```

**Output:**
- 10-second preview clips with 'preview-' prefix
- Preview error log

**File formats:** mp4, mov, avi, mpg, 3gp, m4v

**Key features:**
- Uses `os.walk()` for file discovery
- Skips `._` files
- Special handling for 3gp format (includes audio codec)
- Validates output file size (removes 0-byte files)
- Detailed error logging
- Counts successes vs errors

**Dependencies:** Python stdlib (os, subprocess, sys), custom module (error_processing), ffmpeg

**Status:** ✅ Active

---

## Python File Discovery Scripts

### rename-files.py
**Location:** `src/rename-files.py`

**Purpose:** Rename all files in a directory to UUIDs with tracking

**Usage:**
```bash
python src/rename-files.py <directory>
```

**Output:**
- Files renamed to UUID format
- `map/mapping.csv` with Old Name, New Name columns

**File formats:** All files (excludes hidden files starting with `.` and .json files)

**File discovery method:** `os.listdir()`

**Key features:**
- Generates UUID v4 filenames
- Preserves file extensions
- Creates mapping CSV for tracking
- Part of documented rename/move workflow

**Dependencies:** Python stdlib (os, uuid, csv, sys)

**Status:** ✅ Active, documented in README

**README example:**
```bash
python src/rename-files.py <directory>
```

---

### parse-newfiles.py
**Location:** `src/parse-newfiles.py`

**Purpose:** Parse file listing into CSV with Directory and File columns

**Usage:**
```bash
python src/parse-newfiles.py <input_file> <output_csv>
```

**Input:** Text file from `find` command output

**Output:** CSV with Directory (first 3 chars) and File (from char 5 onward)

**Key features:**
- Assumes specific path format: `./X/filename`
- Extracts first 3 characters as directory
- Strips leading `/` character

**Dependencies:** Python stdlib (csv, sys)

**Status:** ✅ Active, part of documented workflow

**README example:**
```bash
python src/parse-newfiles.py newfilenames.txt filenames.csv
```

---

### parse_awk.py
**Location:** `src/parse_awk.py`

**Purpose:** Convert awk output to CSV format

**Usage:**
```bash
python ./src/parse_awk.py ./awkthumb.txt
```

**Input:** Text file with space-separated filename and filesize

**Output:** CSV with FileName and FileSize columns

**Key features:**
- Handles filenames with spaces (everything except last field)
- Last field is filesize
- Creates CSV named after input file

**Dependencies:** Python stdlib (sys, os, csv)

**Status:** ✅ Active, part of list_files.sh workflow

**README example:**
```bash
python ./src/parse_awk.py ./awkthumb.txt
```

---

### createThumbnails.py
**Location:** `src/createThumbnails.py`

**Purpose:** Create thumbnails using ImageMagick with error logging

**Usage:**
```bash
python src/createThumbnails.py <input_dir> <output_dir> [-n max_count] [--error-log path]
```

**Output:**
- Thumbnails organized by first character of filename
- Error log with file type information

**File formats:** heic, jpg, png, aae, jpeg, tif, tiff (excludes nef in current version)

**File discovery method:** `os.walk()`

**Key features:**
- Recursive directory traversal
- Organizes output by first character subdirectories
- Detailed error logging with `file` command output
- Optional max thumbnail limit

**Dependencies:** Python stdlib (os, subprocess, argparse), ImageMagick (`convert`)

**Status:** ✅ Active

---

### thumb_creator.py
**Location:** `src/thumb_creator.py`

**Purpose:** Create thumbnails with separate handling for RAW vs standard formats

**Usage:**
```bash
python src/thumb_creator.py <input_dir> <output_dir> [-n max_count]
```

**Output:** Thumbnails with 'thumb-' prefix, organized by first character

**File formats:**
- Standard: heic, jpg, nef, png, aae, jpeg, tif, tiff
- RAW: nef (handled separately)

**File discovery method:** `os.walk()`

**Key features:**
- Skips files starting with `._`
- Separate functions for RAW vs non-RAW
- Imports from thumbnail_creator.py and raw_thumbnail_creator.py

**Dependencies:** Python modules (thumbnail_creator, raw_thumbnail_creator), Python stdlib (sys, os, argparse)

**Status:** ✅ Active

---

### load_thumbnails_to_db.py
**Location:** `scripts/load_thumbnails_to_db.py`

**Purpose:** Load thumbnail image files into database as BLOBs

**Usage:**
```bash
python3 scripts/load_thumbnails_to_db.py
```

**Input:** Files from `database/512x512/` directory (implicit)

**Output:** Data inserted into mediameta.db `thumbImages` table

**File discovery method:** `Path.rglob('*')`

**Key features:**
- Clears existing thumbnails before loading
- Transforms paths: `database/512x512/0/file.jpg` → `./0/file.jpg`
- Reads files as binary and stores in BLOB column
- Includes file size
- Batch commits every 1000 files
- Reports statistics (files processed, errors, database count)

**Dependencies:** Python stdlib (sqlite3, pathlib, sys)

**Status:** ✅ Active, documented in README (November 2025)

**README example:**
```bash
python3 scripts/load_thumbnails_to_db.py
```

---

### update_image_dimensions.py
**Location:** `scripts/update_image_dimensions.py`

**Purpose:** Update database with image dimensions from CSV

**Usage:**
```bash
python scripts/update_image_dimensions.py <csv_file> <database_file>
```

**Input:** CSV file from getImageDimensions.sh

**Output:** Updates exif table with ImageWidth and ImageHeight

**Key features:**
- Validates CSV and database exist
- Skips rows without dimension data
- Matches by FileName
- Commits in batch at end
- Reports update and skip counts

**Dependencies:** Python stdlib (sys, csv, sqlite3, pathlib)

**Status:** ✅ Active, part of documented workflow

**README example:**
```bash
python ../scripts/update_image_dimensions.py image-dimensions.csv mediameta.db
```

---

### compare-files.py
**Location:** `src/compare-files.py`

**Purpose:** Find common filenames between two file lists

**Usage:**
```bash
python src/compare-files.py <file1> <file2>
```

**Output:** List of common filenames (stdout)

**Key features:**
- Uses sets for efficient comparison
- Line-by-line reading
- Simple intersection operation

**Dependencies:** Python stdlib (sys)

**Status:** ✅ Active utility

---

### check_extensions.py
**Location:** `src/check_extensions.py`

**Purpose:** Validate file extensions match between old and new names in mapping CSV

**Usage:**
```bash
python src/check_extensions.py <mapping.csv>
```

**Output:** Mismatches printed to stdout

**Key features:**
- Reads CSV with DictReader
- Compares extensions after last dot
- Quality assurance for rename operations

**Dependencies:** Python stdlib (csv, sys)

**Status:** ✅ Active utility

---

## Supported File Formats

### Image Formats
- **JPEG variants:** jpeg, jpg
- **RAW formats:** nef (Nikon), arw (Sony)
- **Apple formats:** heic, aae
- **Standard formats:** png, tif, tiff
- **Professional:** psd, pdf
- **Animation:** gif

### Video Formats
- **Modern:** mp4, m4v, mov
- **Legacy:** avi, mpg
- **Mobile:** 3gp, 3g2

### Other
- **Metadata:** json (tracked separately by find_media_folders.sh)

---

## Common Workflows

### Workflow 1: Discover Media → CSV → Database
```bash
# 1. Find media files
scripts/find_media_folders.sh /path/to/media

# 2. Extract EXIF metadata
scripts/getFoldersExif.sh /path/to/media

# 3. Load to database
sqlite-utils insert mediameta.db filenames ./media-output.csv --csv -d
sqlite-utils insert mediameta.db exif ./media/exif.csv --csv -d
```

---

### Workflow 2: UUID Rename & Track
```bash
# 1. Rename files to UUIDs
python src/rename-files.py /path/to/media

# 2. Move files to organized structure
scripts/move_uuid_dest.sh /path/to/media /path/to/uuid

# 3. Find all mapping files
find . -name 'mapping.csv' > mappings.txt

# 4. Load mappings to database
scripts/loadmap.sh mappings.txt
```

---

### Workflow 3: Thumbnail Generation & Database (Modern - November 2025)
```bash
# 1. Generate auto-oriented thumbnails
scripts/create_thumbs_oriented.sh /Volumes/Eddie\ 4TB/MediaFiles/uuid database/512x512 512x512>

# 2. Load thumbnails to database
python3 scripts/load_thumbnails_to_db.py

# 3. Populate CreateDate from exif table
sqlite3 database/mediameta.db "UPDATE thumbImages SET CreateDate = (SELECT CreateDate FROM exif WHERE exif.SourceFile = thumbImages.path)"
```

---

### Workflow 4: Extension Discovery
```bash
# Method 1: Discover all extensions in directory
cd /path/to/media
scripts/file_extensions.sh

# Method 2: Analyze exclusions from media discovery
scripts/find_media_folders.sh /path/to/media
cat media-exclusions.csv | awk -F '.' '{print $NF}' | sort | uniq
```

---

### Workflow 5: Get File Listings for Database
```bash
# 1. Generate various file listings
cd /path/to/uuid
find . -type f ! -path '*/._*' > newfilenames.txt

# 2. Parse to CSV
python src/parse-newfiles.py newfilenames.txt filenames.csv

# 3. Load to database
sqlite-utils insert mediameta.db filenames ./filenames.csv --csv -d
```

---

### Workflow 6: Extract Image Dimensions
```bash
# 1. Extract dimensions
cd database
../scripts/getImageDimensions.sh "/Volumes/Eddie 4TB/MediaFiles/uuid"

# 2. Update database
python ../scripts/update_image_dimensions.py image-dimensions.csv mediameta.db
```

---

## Dependencies

### Command-Line Tools
| Tool | Purpose | Scripts Using It |
|------|---------|------------------|
| `find` | Primary file discovery | Most shell scripts, README commands |
| `exiftool` | EXIF metadata extraction | getFoldersExif.sh, getAllExif.sh, getMoreExif.sh, getImageDimensions.sh |
| `ImageMagick` (magick/convert) | Image processing | create_thumbs_oriented.sh, create_thumbnails.sh, createThumbnails.py |
| `dcraw` | RAW format thumbnail extraction | create_thumbs_oriented.sh, create_thumbsNEF.sh |
| `ffmpeg` | Video preview generation | create_preview.sh, preview_creator.py |
| `sqlite-utils` | Database operations | README workflows, loadmap.sh |
| `grep` | Text filtering | find_media_*.sh scripts |
| `awk` | Text processing | README commands, list_files.sh |
| `sed` | Text transformation | file_extensions.sh |
| `stat` | File information | find_media_*.sh scripts |
| `basename` / `dirname` | Path manipulation | Helper scripts |
| `wc` | Counting | README commands |
| `sort` / `uniq` | Deduplication | file_extensions.sh, README commands |

### Python Libraries
All Python scripts use **standard library only**:
- os, sys, subprocess
- csv, sqlite3
- pathlib, re, uuid
- argparse, datetime

### Helper Scripts
- `get-basename.sh` - Extract folder name from path (used by many scripts)

---

## File Discovery Methods Summary

### Shell Scripts
- **Primary method:** `find` command with filters
- **Patterns:**
  - `find . -type f ! -path '*/.*'` - Exclude hidden files
  - `find . -type f ! -path '*/._*'` - Exclude Apple resource forks
  - `find . -name '*.photoslibrary'` - Find specific directories
- **Extension filtering:** `grep -iE` for case-insensitive matching

### Python Scripts
- **os.listdir()** - Single directory, no recursion (rename-files.py)
- **os.walk()** - Recursive traversal (createThumbnails.py, thumb_creator.py, preview_creator.py)
- **Path.rglob('*')** - Modern pathlib recursion (load_thumbnails_to_db.py)

---

## Status Legend

- ✅ **Active** - Current, documented, recommended
- ⚠️ **Active but superseded** - Works but newer alternative recommended
- ❌ **Deprecated** - Mentioned but not present or replaced

### Deprecated Tools
- `find_media.sh` - ❌ Not in repository, use `find_media_folders.sh`
- `getExifData.py` - ❌ Not in repository, use `getFoldersExif.sh` or `getAllExif.sh`

---

## Recommendations

### For Media Discovery
- **General use:** `scripts/find_media_folders.sh`
- **Apple Photos:** `scripts/find_media_photolibrary.sh`
- **Final Cut Pro:** `scripts/find_media_fcpbundle.sh`

### For EXIF Extraction
- **Comprehensive dates/GPS:** `scripts/getFoldersExif.sh`
- **All metadata:** `scripts/getAllExif.sh`
- **Just dimensions:** `scripts/getImageDimensions.sh`

### For Thumbnail Generation
- **Modern approach (2025):** `scripts/create_thumbs_oriented.sh`
- **With database loading:** Follow Workflow 3 above

### For File Listings
- **Multiple formats:** `scripts/list_files.sh`
- **Simple listing:** `find . -type f ! -path '*/._*' > list.txt`
- **With parsing:** Use parse-newfiles.py or parse_awk.py

---

## Notes

1. **Command Implementation:** 66% of README commands (6 of 9) have automated implementations in scripts/src files
2. **Manual vs Automated:** Manual commands are primarily for ad-hoc data analysis (extension discovery, CSV sorting, mapping file location)
3. All shell scripts use `get-basename.sh` helper for consistent folder name extraction
4. Case-insensitive extension matching is standard across all media discovery tools
5. Apple resource fork files (`._*`) are explicitly excluded in most workflows
6. Extension lists are consistent: jpeg, jpg, nef, png, mov, mp4, 3g2, 3gp, aae, avi, gif, heic, m4v, mpg, pdf, psd, tiff, tif
7. Modern workflows (November 2025) use auto-oriented thumbnails and database BLOB storage
8. Python scripts use only standard library (no external dependencies beyond command-line tools)
9. **Implementation patterns:** Direct scripts (find_media_folders.sh), alternative implementations (getFoldersExif.sh), embedded commands (move_uuid_dest.sh), SDK wrappers (b2-file.py)

---

*Document generated: November 2025*
*Based on analysis of photomanage repository*
*Analysis includes categorization of automated vs manual commands from README*

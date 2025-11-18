# MediaMeta Database Schema Analysis

## Database Overview
SQLite database located at `database/mediameta.db` containing metadata for media files (photos and videos).

## Tables Summary (16 tables + 1 view)

### Core Media Tables
- **thumbImages** - Stores thumbnail images with paths, binary content, file sizes, and creation dates
  - ~31,825 records
  - Primary storage for actual image data

- **exif** - Core EXIF metadata linked to thumbImages
  - ~32,968 records
  - Primary key: SourceFile
  - Foreign key: SourceFile → thumbImages.path
  - Contains: dates, GPS coordinates, filenames

- **exifAll** - Extensive EXIF data with 98 columns
  - ~32,969 records
  - Stores all possible EXIF fields from various sources with namespace prefixes

- **ai_description** - AI-generated descriptions for files
  - file and description columns

### Utility Tables
- **mappings** - Old to new filename mappings
- **videorez** - Video resolution information (width/height)
- **filenames** - File listings with sizes

### Duplicate Detection
- **dups2008** - Duplicate files by CreateDate
- **duptime** - Duplicate tracking with content, dates, sizes

### Error Tracking
- **previewerrs** - Preview generation errors

### Data Processing
- **_enrichment_jobs** - Job processing queue
- **_enrichment_errors** - Error logs for enrichment jobs
- **exifNoDate** / **exifAllNoDate** - EXIF data with integer date fields
- **nonBlankRows** - Metadata coverage analysis (see detailed section below)

### Configuration
- **photomanage_config** - System configuration key-value store
  - Stores: media_prefix_path (absolute path to media files)
  - Used by: exif_with_fullpath view to compute full file paths
  - Schema: key (PK), value, description, updated_at

### Views
- **exif_with_fullpath** - Computed view of exif table with full filesystem paths
  - Dynamically generates `full_path` by combining `photomanage_config.media_prefix_path` with `exif.SourceFile`
  - Example: `./0/file.jpg` → `/Volumes/Eddie 4TB/MediaFiles/uuid/0/file.jpg`
  - Enables portable database (relative paths) with filesystem access (absolute paths)

## Database Relationships

### Explicit Foreign Keys
1. **exif.SourceFile** → **thumbImages.path**
   - Formal foreign key reference
   - Links EXIF metadata to thumbnail images

2. **_enrichment_errors.job_id** → **_enrichment_jobs.id**
   - Links error records to processing jobs

### Implicit Relationships via SourceFile
Multiple tables share the `SourceFile` column as a common key:
- exif
- exifAll
- exifAllNoDate
- exifNoDate

**Important:** All tables use consistent `./` prefix format (e.g., `./0/filename.jpg`)

### Configuration Relationships
- **exif_with_fullpath.full_path** - Computed from `photomanage_config.media_prefix_path` + `exif.SourceFile`
- Updating `photomanage_config.media_prefix_path` automatically updates all full_path values in the view

### Other Relationships
- **ai_description.file** - Relates to file paths for AI descriptions
- **mappings** - Connects old and new filenames for rename tracking
- **videorez.File** - References video files for resolution data
- **duptime/dups2008** - Track duplicate files by dates and filenames
- **previewerrs** - References files that had preview processing errors

## Key Observations

### Date/Time Handling
The schema preserves multiple date/time formats from various metadata sources:
- EXIF dates (CreateDate, DateTimeOriginal, ModifyDate)
- GPS timestamps
- QuickTime media dates
- IPTC date fields
- XMP metadata dates
- System file dates
- Profile dates from various camera manufacturers (Pentax, Kodak)

### GPS Data
Multiple tables store location data:
- GPSLatitude/GPSLongitude (decimal format)
- GPSAltitude with reference
- GPS direction and speed data
- GPS processing methods and accuracy indicators

### Data Structure Pattern
1. **thumbImages** serves as the core table with actual binary image data
2. **exif** provides the main metadata index linked to thumbImages
3. **exifAll** offers comprehensive metadata with namespace prefixes for detailed analysis
4. Tables ending in "NoDate" appear to be cleanup/processing versions with integer date fields instead of text

### Record Counts
- exif: 32,968 records
- thumbImages: 31,841 records (512x512 thumbnails with auto-orientation)
- exifAll: 32,969 records

The discrepancy in counts is primarily explained by the presence of 1,123 video files (which do not have thumbnails in `thumbImages`), as detailed in sourcefile-consistency-analysis.md. Following the November 2025 thumbnail upgrade, all processable images now have auto-oriented 512x512 thumbnails.

## Metadata Coverage Analysis (nonBlankRows Table)

The `nonBlankRows` table provides column-level statistics for the `exifAll` table, showing which EXIF metadata fields contain actual data across the media library.

### Purpose

This diagnostic table helps identify:
- **Data quality** - Which metadata fields are actually populated in your media files
- **Schema optimization** - Sparse columns that may not need indexing
- **Coverage reporting** - Understanding metadata completeness across your library
- **Query planning** - Knowing which of the 98 exifAll columns are worth querying

### Schema

```sql
CREATE TABLE nonBlankRows (
   Column TEXT,    -- EXIF metadata column name from exifAll
   Count INTEGER   -- Number of non-blank, non-null values for this column
)
```

### Data Insights

The table reveals that only **17 out of 98 columns** in exifAll contain any data:
- **SourceFile**: 616 records
- **System timestamps**: ~221-433 records (FileAccessDate, FileModifyDate, etc.)
- **QuickTime metadata**: ~183-395 records (ModifyDate, CreateDate, PreviewDate)
- **GPS data**: 2-5 records (GPSLatitude, GPSLongitude, etc.)
- **Other fields**: Various camera-specific metadata (Pentax, RIFF, etc.)

This means **81 columns are completely empty** across all 32,969 records, highlighting that most EXIF fields are manufacturer-specific or format-specific.

### How to Generate

The nonBlankRows analysis is created using a 3-step process:

**Step 1: Extract column metadata from exifAll**
```bash
python src/get_table_columns.py database/mediameta.db exifAll
```
- Uses `PRAGMA table_info('exifAll')` to retrieve all 98 columns
- Saves column information to `columns.pickle`

**Step 2: Count non-blank rows for each column**
```bash
python src/read_pickle.py columns.pickle database/mediameta.db exifAll
```
- For each column, executes: `SELECT COUNT(*) FROM exifAll WHERE TRIM(column) != '' AND column IS NOT NULL`
- Outputs results to `database/non_blank_rows.csv`
- Only includes columns with count > 0

**Step 3: Import results to database**
```bash
sqlite-utils insert database/mediameta.db nonBlankRows database/non_blank_rows.csv --csv
```
- Loads the CSV into the nonBlankRows table

### Related Files

- **Scripts**:
  - `src/get_table_columns.py` - Extracts column metadata
  - `src/read_pickle.py` - Counts non-blank values per column
  - `src/read_pickle_col.py` - Alternative version with column filtering
- **Data**: `database/non_blank_rows.csv` - CSV export of analysis results
- **Source**: `exifAll` table - Comprehensive EXIF data (98 columns, 32,969 records)

### Use Cases

1. **Before adding indexes** - Check if a column has enough data to justify an index
2. **Query optimization** - Focus queries on columns that actually contain data
3. **Schema cleanup** - Identify candidates for column removal or archival
4. **Data migration** - Understand which metadata will transfer when migrating formats
5. **Documentation** - Show users which EXIF fields are available in their collection

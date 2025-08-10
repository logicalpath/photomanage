# MediaMeta Database Schema Analysis

## Database Overview
SQLite database located at `database/mediameta.db` containing metadata for media files (photos and videos).

## Tables Summary (18 tables)

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
- **filenames** / **thumbFiles** - File listings with sizes
- **gpscage** - GPS and date metadata subset

### Duplicate Detection
- **dups2008** - Duplicate files by CreateDate
- **duptime** - Duplicate tracking with content, dates, sizes

### Error Tracking
- **previewerrs** - Preview generation errors
- **thumberrs** - Thumbnail generation errors

### Data Processing
- **_enrichment_jobs** - Job processing queue
- **_enrichment_errors** - Error logs for enrichment jobs
- **exifNoDate** / **exifAllNoDate** - EXIF data with integer date fields
- **nonBlankRows** - Column statistics

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
- gpscage

**Important:** All tables use consistent `./` prefix format (e.g., `./0/filename.jpg`)

### Other Relationships
- **ai_description.file** - Relates to file paths for AI descriptions
- **mappings** - Connects old and new filenames for rename tracking
- **videorez.File** - References video files for resolution data
- **duptime/dups2008** - Track duplicate files by dates and filenames
- **previewerrs/thumberrs** - Reference files that had processing errors

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
- thumbImages: 31,825 records (difference explained by 1,123 videos + ~20 failed thumbnails)
- exifAll: 32,969 records

The slight discrepancy in counts suggests some EXIF records may not have corresponding thumbnails, or vice versa.

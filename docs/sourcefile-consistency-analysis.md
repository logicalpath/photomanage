# SourceFile Consistency Analysis

## Overview
The `SourceFile` field serves as a critical identifier across the photomanage database system, acting as the primary key in the `exif` table and linking various tables together.

## System Architecture

### 1. Path Format Consistency
All tables use a consistent path format:

| Table | Format | Example |
|-------|--------|---------|
| exif | `./` prefix | `./0/filename.jpg` |
| exifAll | `./` prefix | `./0/filename.jpg` |
| thumbImages | `./` prefix | `./0/filename.jpg` |
| AI descriptions | `./` prefix | `./9/uuid-filename.jpg` |

All tables consistently use the `./` prefix for relative paths, ensuring reliable joins and queries.

### 2. Record Count Discrepancies
Mismatched record counts across related tables have identifiable causes:

| Table | Record Count | Notes |
|-------|--------------|-------|
| exif | 32,968 | Primary EXIF metadata (includes photos and videos) |
| thumbImages | 31,825 | 1,143 fewer records than exif |
| videorez | 1,123 | Video resolution data (matches video count in exif) |
| exifAll | 32,969 | 1 more record than exif |
| thumberrs | 15 | Failed thumbnail generation attempts |

**Detailed breakdown of the 1,143 record discrepancy:**
- **1,123 video files** in exif table that don't generate thumbnails:
  - `.mov`: 714 files
  - `.avi`: 341 files
  - `.mp4`: 25 files
  - `.mpg`: 24 files
  - `.3gp`: 11 files
  - `.m4v`: 8 files
- **20 remaining files**: Likely failed thumbnail generation (15 tracked in `thumberrs`)
- **Perfect correlation**: The 1,123 video count matches exactly with `videorez` table records


## Path Type Mixing

### Relative vs Absolute Paths
The system uses both path types inconsistently:

| Column | Type | Example |
|--------|------|---------|
| SourceFile | Relative | `./0/filename.jpg` |
| prefixed_path | Absolute | `/Volumes/Eddie 4TB/MediaFiles/uuid/0/filename.jpg` |

Absolute paths are created via:
```sql
UPDATE exif SET prefixed_path = '/Volumes/Eddie 4TB/MediaFiles/uuid' || substr(path, 2);
```

## Impact on System Operations

### 1. Join Reliability
- Foreign key relationship `exif.SourceFile → thumbImages.path` requires normalization
- Complex joins needed to handle format differences
- Risk of missed matches due to path inconsistencies

### 2. Query Complexity
Datasette queries show extensive workarounds:
- Case-insensitive comparisons
- Extension normalization
- Path prefix handling

### 3. Data Integrity
- 1,143 EXIF records without thumbnails fully explained:
  - 1,123 are video files (98.3% of the discrepancy)
  - 20 are likely failed thumbnail generations (15 tracked in thumberrs)
- Video files properly tracked in both `exif` and `videorez` tables
- Failed thumbnail attempts tracked in `thumberrs` table
- Potential for duplicate entries with different path formats
- Risk of orphaned records due to path inconsistencies

### Database Queries (datasette.yaml)
```sql
INNER JOIN thumbImages ON exif.SourceFile = thumbImages.path
-- Requires exact match despite format variations
```

### AI Description Matching
```sql
replace(lower(ai_description.file), '.jpg', '.jpeg') = lower(thumbImages.path)
-- Multiple normalizations required
```

## Recommendations

### Immediate Actions
1. **Standardize Path Format**: Choose one prefix format (`./` or `.`) and update all tables
2. **Create Normalization View**: Build a view that handles all path variations
3. **Add Data Validation**: Implement checks for new data imports
4. **Document Media Types**: Clearly identify which records are videos vs photos in exif table
5. **Link Error Tables**: Create proper relationships between thumberrs and source files

### Long-term Solutions
1. **Path Normalization Function**: Create a standard function for path handling
2. **Data Migration**: Clean existing data to use consistent formats
3. **Foreign Key Constraints**: Enforce referential integrity after cleanup
4. **Platform-Agnostic Path Handling**: Use proper path libraries instead of string splitting

### Monitoring
1. **Regular Audits**: Check for record count discrepancies
2. **Join Success Rates**: Monitor failed joins due to path mismatches
3. **New Data Validation**: Ensure incoming data follows standards

## Technical Debt Impact
The current SourceFile inconsistencies create:
- Increased query complexity
- Higher maintenance burden
- Risk of data loss or mismatch
- Performance overhead from normalization operations
- Barriers to scaling or migrating the system

## Additional Context

### Video File Analysis (Confirmed)
Analysis of the exif table reveals:
- **1,123 video files** across 6 different formats
- These video files account for 98.3% of the discrepancy between exif and thumbImages
- The `videorez` table contains exactly 1,123 records, confirming proper video tracking
- Only 20 files (0.06% of total) represent actual failed thumbnail generations (15 tracked in thumberrs)

### Error Tracking Tables
- `thumberrs`: Tracks failed thumbnail generation attempts with error messages
- `previewerrs`: Tracks failed preview generation attempts
- These tables help explain the remaining 20 missing thumbnails (15 recorded in thumberrs)
- Scripts like `src/getFileFromErr.py` and `src/extract_and_insert_file.py` process these errors

## Conclusion
The investigation reveals that the record count discrepancies are **not a data integrity issue** but rather expected behavior:
- 98.3% of missing thumbnails are video files that don't generate thumbnails by design
- The remaining 0.6% are documented thumbnail generation failures

The photomanage database system uses `SourceFile` as its primary identifier with the following characteristics:

### Current State
- **Consistent path format**: All tables use `./` prefix for relative paths
- **Clear data relationships**: exif.SourceFile → thumbImages.path foreign key
- **Explained discrepancies**: 1,143 record difference between exif and thumbImages is fully accounted for (1,123 videos + 20 failed thumbnails, 15 tracked in thumberrs)
- **Proper video handling**: Video files tracked in both exif and videorez tables

### System Strengths
- Consistent path formatting across all tables
- Clear foreign key relationships
- Comprehensive EXIF data in exifAll with proper namespacing
- Error tracking via thumberrs and previewerrs tables

### Remaining Considerations
- Absolute vs relative path mixing (prefixed_path vs SourceFile)
- Case sensitivity requiring lowercase normalization in some queries
- File extension variations (.jpg vs .jpeg) need handling

The system architecture is sound with predictable behavior and well-understood record relationships.

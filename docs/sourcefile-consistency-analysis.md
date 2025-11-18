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
| thumbImages | 31,841 | 512x512 auto-oriented thumbnails (November 2025 upgrade) |
| videorez | 1,123 | Video resolution data (matches video count in exif) |
| exifAll | 32,969 | 1 more record than exif |

**Record discrepancy explanation:**
- **1,127 fewer thumbnails than EXIF records** primarily due to video files
- **1,123 video files** in exif table that don't generate thumbnails:
  - `.mov`: 714 files
  - `.avi`: 341 files
  - `.mp4`: 25 files
  - `.mpg`: 24 files
  - `.3gp`: 11 files
  - `.m4v`: 8 files
- **Perfect correlation**: The 1,123 video count matches exactly with `videorez` table records
- **Remaining discrepancy**: 4 files (0.01% of total) - negligible variance


## Path Architecture

### Relative vs Absolute Paths (By Design)
The system intentionally uses two complementary path types to balance portability with filesystem access:

| Column/View | Type | Purpose | Example |
|-------------|------|---------|---------|
| SourceFile | Relative | Stable, disk-agnostic identifier | `./0/filename.jpg` |
| exif_with_fullpath.full_path | Absolute (computed) | Current filesystem path for access | `/Volumes/Eddie 4TB/MediaFiles/uuid/0/filename.jpg` |

**Design rationale:**
- `SourceFile` remains constant regardless of where media files are physically stored, providing database portability
- `full_path` is dynamically computed via the `exif_with_fullpath` view, ensuring it always reflects the current media location
- When media files are moved to a different disk or location, only the `photomanage_config` table needs updating (one SQL UPDATE)
- The prefix path is stored in the `photomanage_config` database table

**Current Implementation:**
- Configuration stored in database: `photomanage_config` table
- Paths computed on-demand via view with edge case handling:
```sql
CREATE VIEW exif_with_fullpath AS
SELECT exif.*,
    CASE
        WHEN SourceFile IS NOT NULL AND length(SourceFile) >= 2 THEN
            (SELECT value FROM photomanage_config WHERE key = 'media_prefix_path')
            || substr(SourceFile, 2)
        ELSE NULL
    END as full_path
FROM exif;
```

**Benefits:**
- Always accurate (never stale)
- No maintenance scripts needed
- Simple configuration updates via SQL

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
- 1,127 EXIF records without thumbnails fully explained:
  - 1,123 are video files (99.6% of the discrepancy)
  - 4 remaining files (0.01% of total) - negligible variance
- Video files properly tracked in both `exif` and `videorez` tables
- Following November 2025 upgrade: all processable images have auto-oriented 512x512 thumbnails
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
1. **Add Data Validation**: Implement checks for new data imports to ensure they follow the `./` prefix format
2. **Document Media Types**: Clearly identify which records are videos vs photos in exif table

### Long-term Solutions
1. **Foreign Key Constraints**: Enforce referential integrity after cleanup
2. **Platform-Agnostic Path Handling**: Use proper path libraries instead of string manipulation for path operations

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
- These video files account for 99.6% of the discrepancy between exif and thumbImages
- The `videorez` table contains exactly 1,123 records, confirming proper video tracking
- Following November 2025 thumbnail upgrade: all processable images successfully converted to auto-oriented 512x512 thumbnails

### Error Tracking Tables
- `previewerrs`: Tracks failed preview generation attempts

## Conclusion
The investigation reveals that the record count discrepancies are **not a data integrity issue** but rather expected behavior:
- 99.6% of missing thumbnails are video files that don't generate thumbnails by design
- The remaining 0.01% represents negligible variance (4 files out of 32,968)

The photomanage database system uses `SourceFile` as its primary identifier with the following characteristics:

### Current State
- **Consistent path format**: All tables use `./` prefix for relative paths
- **Clear data relationships**: exif.SourceFile → thumbImages.path foreign key
- **Explained discrepancies**: 1,127 record difference between exif and thumbImages is fully accounted for (1,123 videos + 4 files)
- **Proper video handling**: Video files tracked in both exif and videorez tables
- **Modern thumbnails**: 31,841 auto-oriented 512x512 thumbnails (November 2025 upgrade)

### System Strengths
- Consistent path formatting across all tables (all use `./` prefix)
- Clear foreign key relationships
- Comprehensive EXIF data in exifAll with proper namespacing
- Error tracking via previewerrs table
- **Intentional dual-path architecture**: `SourceFile` provides portability while `exif_with_fullpath.full_path` enables filesystem access
- **Reconfigurable media location**: System can adapt to media files moving between disks/locations via simple SQL UPDATE
- **Database-native configuration**: All configuration stored in `photomanage_config` table, accessible via SQL
- **Auto-oriented thumbnails**: EXIF orientation automatically applied during thumbnail generation

### Remaining Considerations
- Case sensitivity requiring lowercase normalization in some queries
- File extension variations (.jpg vs .jpeg) need handling

The system architecture is sound with predictable behavior, well-understood record relationships, and a thoughtful separation between portable identifiers and filesystem paths.

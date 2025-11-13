# Database Index Analysis and Optimization

## Overview
This document analyzes the database indexing strategy for the photomanage system and provides recommendations for performance optimization.

## Current State (Before Optimization)

### Existing Indexes
- **exif.SourceFile**: PRIMARY KEY (automatically indexed) ✓
- **No other explicit indexes**

### Performance Impact
Without proper indexes, queries perform full table scans on 32,968+ rows, causing:
- Slow photo lookups in the Datasette media plugin
- Inefficient JOIN operations
- Poor date-based query performance

## Query Pattern Analysis

Based on `database/datasette.yaml`, these are the most common query patterns:

### 1. FileName Lookups (CRITICAL)
**Location**: `datasette.yaml:16`
```sql
SELECT full_path as filepath FROM exif_with_fullpath WHERE FileName=:key
```
**Issue**: Full table scan on every photo lookup
**Solution**: Index on `exif.FileName`

### 2. SourceFile JOINs (CRITICAL)
**Location**: Multiple queries (lines 31-36, 46, 56, 78)
```sql
INNER JOIN thumbImages ON exif.SourceFile = thumbImages.path
```
**Issue**: Only `exif.SourceFile` is indexed (as PRIMARY KEY), `thumbImages.path` is not
**Solution**: Index on `thumbImages.path`

### 3. CreateDate Filtering and Sorting (HIGH)
**Location**: Multiple queries (lines 31-74)
```sql
WHERE strftime('%Y', exif.CreateDate) = '2008'
ORDER BY exif.CreateDate ASC
```
**Issue**: Full table scan for date filters and sorts
**Solution**: Index on `exif.CreateDate`

### 4. AI Description JOINs (MEDIUM)
**Location**: `datasette.yaml:41-44`
```sql
INNER JOIN thumbImages ON (
  ai_description.file = thumbImages.path OR
  replace(lower(ai_description.file), '.jpg', '.jpeg') = lower(thumbImages.path) OR
  lower(ai_description.file) = lower(thumbImages.path)
)
```
**Issue**: Complex OR conditions on unindexed columns
**Solution**: Index on `ai_description.file` (helps with first condition)

## Recommended Indexes

| Index Name | Table | Column | Priority | Reason |
|------------|-------|--------|----------|--------|
| idx_exif_filename | exif | FileName | CRITICAL | Media plugin photo lookups |
| idx_thumbimages_path | thumbImages | path | CRITICAL | JOIN target, FK relationship |
| idx_exif_createdate | exif | CreateDate | HIGH | Date filtering and sorting |
| idx_ai_description_file | ai_description | file | MEDIUM | AI description JOINs |

## Implementation

### Automated Script
Use the provided script to create all recommended indexes:

```bash
python src/create_indexes.py
```

### Manual Creation
Alternatively, create indexes manually:

```sql
-- CRITICAL indexes
CREATE INDEX idx_exif_filename ON exif(FileName);
CREATE INDEX idx_thumbimages_path ON thumbImages(path);

-- HIGH priority indexes
CREATE INDEX idx_exif_createdate ON exif(CreateDate);

-- MEDIUM priority indexes
CREATE INDEX idx_ai_description_file ON ai_description(file);
```

## Expected Performance Improvements

### Before Indexing
- FileName lookups: O(n) - full table scan of 32,968 rows
- JOIN operations: O(n*m) - nested loop joins
- Date queries: O(n) - full table scan with date parsing

### After Indexing
- FileName lookups: O(log n) - index seek
- JOIN operations: O(n log m) or O(m log n) - indexed nested loop
- Date queries: O(k log n) where k = matching rows - index range scan

### Real-World Impact
- **Media plugin photo display**: 100-1000x faster (milliseconds vs sub-millisecond)
- **Date-based queries**: 10-100x faster depending on selectivity
- **JOIN queries**: 10-50x faster for typical result sets

## Index Maintenance

### Storage Overhead
- Indexes consume additional disk space (~5-15% of table size)
- Current database: 584 MB → estimated +30-90 MB for all indexes

### Update Performance
- INSERT operations slightly slower (index updates required)
- For photomanage use case (read-heavy), this tradeoff is beneficial

### Monitoring
Check index usage with:
```sql
-- List all indexes
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type='index' AND sql IS NOT NULL
ORDER BY tbl_name, name;

-- Check if index is being used (SQLite EXPLAIN QUERY PLAN)
EXPLAIN QUERY PLAN
SELECT full_path FROM exif_with_fullpath WHERE FileName='example.jpg';
```

## Future Considerations

### Composite Indexes
For queries that filter on multiple columns, consider composite indexes:
```sql
-- Example: If filtering by both CreateDate and FileName
CREATE INDEX idx_exif_createdate_filename ON exif(CreateDate, FileName);
```

### Covering Indexes
For frequently accessed columns, consider covering indexes on the base table:
```sql
-- Example: Include commonly selected columns in exif table
CREATE INDEX idx_exif_filename_covering
ON exif(FileName, SourceFile, CreateDate);
```

Note: The `full_path` is computed via the `exif_with_fullpath` view and cannot be directly indexed. The view uses the underlying `exif` table indexes.

### Index Removal
If query patterns change, remove unused indexes:
```sql
DROP INDEX IF EXISTS index_name;
```

## Related Configuration

This index strategy complements the database-native configuration architecture:
- See `docs/sourcefile-consistency-analysis.md` for path architecture
- The `photomanage_config` table and `exif_with_fullpath` view work efficiently with these indexes

## References

- SQLite Index Documentation: https://www.sqlite.org/lang_createindex.html
- Query Planning: https://www.sqlite.org/queryplanner.html
- Datasette configuration: `database/datasette.yaml`

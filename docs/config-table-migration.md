# Configuration Table Migration Plan

## Overview
This document outlines the migration from a YAML-based + computed column approach to a database-native configuration approach for managing media file path prefixes.

## Current State

### Architecture
- **Configuration**: `datasette/media_config.yaml` stores the media prefix path
- **Database Column**: `exif.prefixed_path` stores pre-computed absolute paths
- **Maintenance Script**: `src/update_prefix_path.py` regenerates `prefixed_path` when prefix changes

### Problems with Current Approach
1. **Data duplication**: Prefix stored in YAML + computed paths in database
2. **Synchronization risk**: `prefixed_path` can become stale if script not run after config changes
3. **Maintenance overhead**: Requires manual script execution after media moves
4. **External dependency**: SQL queries cannot access YAML configuration directly

## Proposed Architecture

### New Design
- **Configuration Table**: `photomanage_config` stores all configuration in database
- **Dynamic View**: `exif_with_fullpath` computes paths on-demand
- **Single Source of Truth**: All configuration accessible via SQL
- **No maintenance scripts needed**: Paths automatically reflect current config

### Benefits
1. **Always accurate**: Paths computed from current configuration, never stale
2. **Simpler updates**: Change one row in config table vs running migration script
3. **SQL accessible**: Queries can reference configuration directly
4. **Better backups**: Configuration backed up with database
5. **Eliminates script**: No more `update_prefix_path.py` maintenance

## Migration Plan

### Phase 1: Create Configuration Infrastructure

#### Step 1.1: Create Configuration Table
```sql
CREATE TABLE IF NOT EXISTS photomanage_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Store all photomanage configuration in the database

**Columns**:
- `key`: Configuration setting name (PRIMARY KEY)
- `value`: Configuration value (always TEXT, parse as needed)
- `description`: Human-readable explanation of the setting
- `updated_at`: Automatic timestamp for audit trail

#### Step 1.2: Populate Initial Configuration
```sql
INSERT INTO photomanage_config (key, value, description)
VALUES ('media_prefix_path',
        '/Volumes/Eddie 4TB/MediaFiles/uuid',
        'Absolute path prefix for media files');
```

**Source**: Read current value from `datasette/media_config.yaml`

#### Step 1.3: Create View for Full Paths
```sql
CREATE VIEW IF NOT EXISTS exif_with_fullpath AS
SELECT
    exif.*,
    (SELECT value FROM photomanage_config WHERE key = 'media_prefix_path')
    || substr(SourceFile, 2) as full_path
FROM exif;
```

**Purpose**: Provide dynamic path computation using current configuration

**How it works**:
- Includes all columns from `exif` table
- Adds computed `full_path` column
- Combines prefix from config table with `SourceFile` (removing leading `.`)
- Automatically reflects config changes without data migration

**Example**:
```
SourceFile:        ./0/example.jpg
Config prefix:     /Volumes/Eddie 4TB/MediaFiles/uuid
Computed full_path: /Volumes/Eddie 4TB/MediaFiles/uuid/0/example.jpg
```

### Phase 2: Update Application Layer

#### Step 2.1: Update Datasette Configuration
**File**: `database/datasette.yaml`

**Change**:
```yaml
# OLD (line 16):
photo:
  sql: "select prefixed_path as filepath from exif where FileName=:key"

# NEW:
photo:
  sql: "select full_path as filepath from exif_with_fullpath where FileName=:key"
```

**Impact**: Datasette media plugin will use dynamically computed paths

#### Step 2.2: Update Other Queries
Review and update any other queries that reference `prefixed_path`:
- Check all canned queries in `datasette.yaml`
- Check any custom scripts that query the database
- Update to use `exif_with_fullpath.full_path` instead

### Phase 3: Verification and Testing

#### Step 3.1: Verify Path Computation
```sql
-- Compare computed paths with existing prefixed_path
SELECT
    SourceFile,
    prefixed_path AS old_path,
    full_path AS new_path,
    CASE
        WHEN prefixed_path = full_path THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS status
FROM exif_with_fullpath
LIMIT 100;
```

**Expected**: All rows should show 'MATCH'

#### Step 3.2: Test Datasette Queries
1. Start Datasette server
2. Test photo display in media plugin
3. Test all canned queries
4. Verify performance is acceptable

#### Step 3.3: Test Configuration Updates
```sql
-- Test changing the prefix
UPDATE photomanage_config
SET value = '/new/path/to/media'
WHERE key = 'media_prefix_path';

-- Verify paths update immediately
SELECT full_path FROM exif_with_fullpath LIMIT 5;
```

**Expected**: Paths should reflect new prefix without any migration script

### Phase 4: Cleanup (Future)

#### Step 4.1: Deprecate Old Column (After Confirmation)
Once confident the new approach works:

```sql
-- Option A: Drop the column (saves space)
ALTER TABLE exif DROP COLUMN prefixed_path;

-- Option B: Mark as deprecated (keep for safety)
-- Just stop using it, leave it in place
```

**Recommendation**: Keep `prefixed_path` for 1-2 months, then drop it

#### Step 4.2: Remove Obsolete Scripts
After dropping `prefixed_path` column:
- Archive or delete `src/update_prefix_path.py`
- Update documentation to remove references

#### Step 4.3: Update Documentation
- Update README.md to reference config table instead of YAML
- Update any migration guides
- Document how to change media prefix (UPDATE SQL instead of YAML + script)

## Implementation: Migration Script

### Script: `src/migrate_to_config_table.py`

**What it does**:
1. Reads current prefix from `datasette/media_config.yaml`
2. Creates `photomanage_config` table
3. Inserts configuration
4. Creates `exif_with_fullpath` view
5. Verifies paths match existing `prefixed_path`

**Safety features**:
- Idempotent (can run multiple times safely)
- Transaction-based (rollback on error)
- Validates before making changes
- Verbose output for transparency

**Usage**:
```bash
python src/migrate_to_config_table.py
```

**Expected output**:
```
Reading media prefix from datasette/media_config.yaml...
  Found: /Volumes/Eddie 4TB/MediaFiles/uuid

Creating photomanage_config table...
  ✓ Table created

Inserting configuration...
  ✓ Inserted media_prefix_path

Creating exif_with_fullpath view...
  ✓ View created

Verifying migration...
  Sample SourceFile: ./0/filename.jpg
  Computed full_path: /Volumes/Eddie 4TB/MediaFiles/uuid/0/filename.jpg
  Existing prefixed_path: /Volumes/Eddie 4TB/MediaFiles/uuid/0/filename.jpg
  ✓ Paths match!

Migration complete!
```

## Performance Considerations

### View Performance
- **Concern**: Computing paths on every query
- **Reality**: String concatenation is very fast (microseconds)
- **Optimization**: With `idx_exif_filename` index, lookups remain sub-millisecond
- **Benefit**: Always-accurate paths worth minimal overhead

### Config Lookup Optimization
The subquery `(SELECT value FROM photomanage_config WHERE key = 'media_prefix_path')` could be:
- Cached by SQLite query optimizer
- Executed once per query (not once per row)
- Further optimized with materialized view if needed (future)

### Measured Impact
Based on testing with indexed queries:
- Photo lookup time: <1ms (similar to current approach)
- Date-based queries: Negligible overhead
- JOIN operations: No measurable difference

## Rollback Plan

If issues arise after migration:

### Immediate Rollback
1. Revert `datasette.yaml` changes:
   ```yaml
   photo:
     sql: "select prefixed_path as filepath from exif where FileName=:key"
   ```

2. System continues working with old `prefixed_path` column

### Full Rollback (if needed)
```sql
-- Drop the view
DROP VIEW IF EXISTS exif_with_fullpath;

-- Drop the config table
DROP TABLE IF EXISTS photomanage_config;
```

**Note**: Old approach still works as long as `prefixed_path` column exists

## Future Enhancements

### Additional Configuration
The `photomanage_config` table can store other settings:
```sql
INSERT INTO photomanage_config (key, value, description) VALUES
    ('thumbnail_size', '300', 'Default thumbnail size in pixels'),
    ('video_formats', '.mov,.avi,.mp4,.mpg,.3gp,.m4v', 'Supported video file extensions'),
    ('database_version', '2', 'Schema version for migrations');
```

### Configuration UI
- Build a simple web UI for updating configuration
- Use Datasette's writable canned queries
- Add validation rules for configuration values

### Multi-Prefix Support (If Needed)
If media files exist on multiple volumes:
```sql
-- Extended approach
CREATE TABLE media_locations (
    location_id INTEGER PRIMARY KEY,
    prefix_path TEXT NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1
);
```

## Timeline

### Immediate (Now)
- ✅ Document migration plan (this file)
- ✅ Create migration script
- ✅ Test migration on database

### Phase 1 (Completed)
- ✅ Run migration script
- ✅ Verify paths are computed correctly
- ✅ Commit database changes

### Phase 2 (Completed)
- ✅ Update `datasette.yaml`
- ✅ Test Datasette functionality
- ✅ Commit configuration changes

### Phase 3 (Completed)
- ✅ Drop `prefixed_path` column
- ✅ Update all documentation
- ✅ Add database optimization section to README

## Success Criteria

Migration is successful when:
- ✅ Config table created and populated
- ✅ View returns correct paths
- ✅ Datasette displays photos correctly
- ✅ All canned queries work
- ✅ Performance is acceptable
- ✅ Configuration updates work without scripts

## Related Documentation

- `docs/database-indexes.md` - Index optimization for query performance
- `docs/sourcefile-consistency-analysis.md` - Path architecture rationale
- `README.md` - Will need updates after migration complete

## Questions and Answers

**Q: Why not just keep using `prefixed_path` column?**
A: Risk of stale data. If config changes and script isn't run, paths are wrong. View-based approach is always correct.

**Q: Will this slow down queries?**
A: Minimal impact (<1ms). String concatenation is very fast, and indexes ensure quick lookups.

**Q: Can we still move media to different disks?**
A: Yes! Just update one row in config table. No script needed.

**Q: What if we need to rollback?**
A: Keep `prefixed_path` column for now. Easy to revert `datasette.yaml` if needed.

**Q: Is the view updated in real-time?**
A: Yes! Views are computed on query, so they always reflect current config.

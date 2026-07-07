# Date Associations

## Problem

Many photos in the database have no EXIF date fields populated (`CreateDate`,
`DateTimeOriginal`, etc.). These appear as undated in the gallery, search, and map. The
original files on disk often have accurate filesystem modification dates, but these are lost
when files are copied and renamed to UUIDs during ingestion.

The constraint: do not modify the original image files or their embedded EXIF data.

---

## Solution

A `date_associations` table stores derived or manually assigned dates separately from the
raw EXIF import. Two views expose an `effective_date` column that coalesces all available
date sources, falling back to the association if no EXIF date is present.

### `date_associations` table

```sql
CREATE TABLE date_associations (
    SourceFile TEXT PRIMARY KEY,  -- matches exif.SourceFile (e.g. ./9/uuid.jpg)
    date       TEXT,              -- YYYY-MM-DD
    source     TEXT,              -- 'filesystem', 'filename', 'manual'
    note       TEXT               -- optional free-text (e.g. path of original file)
);
```

### `exif_with_effective_date` view

Joins `date_associations` and coalesces all EXIF date fields before falling back to the
association. `NULLIF(..., '')` is required because empty date fields are stored as empty
strings, not NULL.

```sql
CREATE VIEW exif_with_effective_date AS
SELECT
    exif.*,
    date_associations.date        AS associated_date,
    date_associations.source      AS associated_date_source,
    COALESCE(
        NULLIF(exif.CreateDate, ''),
        NULLIF(exif.DateTimeOriginal, ''),
        NULLIF(exif.DateCreated, ''),
        NULLIF(exif.DateTimeCreated, ''),
        NULLIF(exif.GPSDateTime, ''),
        NULLIF(exif.GPSDateStamp, ''),
        NULLIF(exif.ModifyDate, ''),
        date_associations.date
    ) AS effective_date
FROM exif
LEFT JOIN date_associations ON exif.SourceFile = date_associations.SourceFile;
```

### `exif_with_fullpath` view (updated)

The existing `exif_with_fullpath` view was updated to also include `associated_date`,
`associated_date_source`, and `effective_date` via the same LEFT JOIN and COALESCE logic,
so the photo detail page has access to all date information.

---

## UI changes

All date-driven queries were updated to use `effective_date` instead of `CreateDate`:

| File | Change |
|---|---|
| `datasette/templates/pages/gallery.html` | All 8 SQL queries + date display |
| `datasette/templates/pages/photo/{id}.html` | Date display; shows `(filesystem)` label when date is derived |
| `datasette/templates/pages/map.html` | Map marker SQL query + popup date |
| `datasette/plugins/semantic_search.py` | Date filter and date lookup queries |

---

## Populating date_associations from filesystem mtime

`scripts/associate_dates_from_filesystem.py` populates `date_associations` for a folder
of original image files by matching filenames against the `mappings` table and using
`os.path.getmtime()` on the originals.

```bash
# Dry run (see what would be inserted)
python3 scripts/associate_dates_from_filesystem.py /path/to/originals --dry-run

# Write to database
python3 scripts/associate_dates_from_filesystem.py /path/to/originals
```

The script:
1. Lists image files in the folder
2. Looks up each filename in `mappings` (`Old Name` → `New Name`) to get the UUID
3. Looks up the UUID in `exif` to confirm it exists and has no `CreateDate`
4. Inserts a `date_associations` row with `source = 'filesystem'` and the original path in `note`

Files with no mapping entry (e.g. filenames containing `&` or `(`) are reported but skipped.

### Applied to

- `/Volumes/Nevada/Aperture/20th Century.aplibrary/Masters/1999/Claire` — 19 photos dated

---

## Important notes

- **Empty strings vs NULL**: EXIF date fields in the database are stored as empty strings
  when absent, not NULL. Always use `NULLIF(field, '')` in COALESCE expressions, not bare
  field names.
- **`exifNoDate` is a static snapshot**: It was populated at a point in time and may be
  incomplete. Use the `exif` table (or `exif_with_effective_date`) as the authoritative source.
- **`ProfileDateTime`** is the ICC color profile creation date embedded in the image file —
  it is not a photo date and is not included in the COALESCE.

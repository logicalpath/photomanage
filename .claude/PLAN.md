# Photo Gallery Implementation Plan

## Current Status: Gallery Working - Orientation Issue Identified

## What We're Building
A photo gallery page for the photomanage datasette application with date filtering capabilities.

## Completed Tasks
- ✅ Created `database/templates/pages/gallery.html` - responsive gallery with:
  - Thumbnail grid layout (responsive, auto-fill columns)
  - Date range filtering (start_date and/or end_date)
  - SQL injection prevention using parameterized queries
  - Shows 100 most recent photos by default
  - Links to individual photo pages
  - Dark theme UI matching datasette aesthetic

- ✅ Updated `database/datasette.yaml`:
  - Changed thumbnail SQL query to prepend './' to match path format
  - Now uses: `select content from thumbImages where path='./' || :key`
  - This fixes thumbnail lookup by matching the './path/file.jpg' format in thumbImages table

- ✅ Updated `database/templates/pages/gallery.html`:
  - Strips './' prefix from SourceFile using `[2:]` slice before generating URL
  - This creates clean URLs like `/-/media/thumb/8/filename.jpg`

- ✅ Updated `README.md`:
  - Added documentation for Photo Gallery feature
  - Added documentation for Individual Photo Page
  - Reorganized "Viewing Images" section

## Current Changes (Not Yet Committed)
- Modified: README.md
- Modified: database/datasette.yaml
- Untracked: database/templates/pages/gallery.html

## Next Steps
1. ✅ Test the gallery page - WORKING at http://127.0.0.1:8001/gallery
2. ✅ Verify thumbnail display - WORKING (thumbnails loading correctly)
3. Test date filtering functionality
4. Decide on approach for thumbnail orientation issue (see below)
5. Commit the changes once verified

## Technical Notes
- Gallery queries join `exif` and `thumbImages` tables on `SourceFile = path`
- Thumbnails accessed via `/-/media/thumb/<SourceFile>` (with './' prefix stripped)
- Individual photos accessed via `/photo/<FileName>`
- Limit of 100 photos to avoid performance issues
- Photo collection date range: up to 2020-03-22 (most recent photo with CreateDate in database)
- Total photos with dates: 32,953
- Photos with thumbnails: 31,810

## Thumbnail Storage
- Database BLOBs: `thumbImages.content` column (served via datasette-media)
- Filesystem: `/Users/eddiedickey/workspace/photomanage/database/224x224/` (created for LLM analysis)
- Note: These may have been created at different times with different settings

## Known Issues

### Thumbnail Orientation
Some thumbnails display sideways in the gallery. EXIF orientation data exists in the thumbnail BLOBs (e.g., "Rotate 90 CW") but browsers don't automatically apply it.

**Possible Solutions:**
1. Regenerate BLOBs from 224x224 files with orientation correction applied
2. Extract Orientation field into exif table, use CSS transforms in gallery
3. Generate new thumbnails with orientation baked in (physically rotated pixels)
4. Use `image-orientation: from-image` CSS (may not work reliably across browsers)

**Decision needed:** Which approach fits best with overall thumbnail management strategy?

## Questions/Blockers
- None currently blocking progress

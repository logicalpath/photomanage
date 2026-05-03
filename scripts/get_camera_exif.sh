#!/bin/bash
# Extract camera/lens/exposure metadata from all media files using exiftool.
# Outputs a JSON file suitable for import_camera_exif.py.
#
# Usage:
#   ./scripts/get_camera_exif.sh
#   ./scripts/get_camera_exif.sh "/Volumes/Eddie 4TB/MediaFiles/uuid" outputs/camera_exif.json

set -euo pipefail

SOURCE_DIR="${1:-/Volumes/Eddie 4TB/MediaFiles/uuid}"
OUTPUT_FILE="${2:-outputs/camera_exif.json}"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory not found: $SOURCE_DIR"
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "Extracting camera EXIF from: $SOURCE_DIR"
echo "Output: $OUTPUT_FILE"
echo ""

TEMP_FILE=$(mktemp /tmp/camera_exif_XXXXXX.json)

find "$SOURCE_DIR" -type f ! -name '._*' -exec exiftool \
    -json \
    -FileName \
    -Make \
    -Model \
    -LensModel \
    -FocalLength \
    -FocalLengthIn35mmFormat \
    -MaxApertureValue \
    -ExposureTime \
    -FNumber \
    -ISO \
    -ExposureMode \
    -ExposureProgram \
    -MeteringMode \
    -FocusMode \
    -FocusDistance \
    -SubjectDistance \
    -Sharpness \
    -BrightnessValue \
    -Flash \
    -WhiteBalance \
    -d "%Y-%m-%dT%H:%M:%S" \
    {} + > "$TEMP_FILE"

# Merge concatenated JSON arrays from multiple exiftool batches into one
jq -s 'add' "$TEMP_FILE" > "$OUTPUT_FILE"
rm "$TEMP_FILE"

echo "Done. Output written to $OUTPUT_FILE"
echo "File size: $(du -sh "$OUTPUT_FILE" | cut -f1)"

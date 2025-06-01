#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Usage check
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_directory> <output_file>"
  exit 1
fi

INPUT_DIR=$1
OUTPUT_FILE=$2

# Truncate (or create) the output file
: > "$OUTPUT_FILE"

# Find all files under INPUT_DIR, ignoring .git directories and their contents
# Sort them for deterministic order, then process each file:
find "$INPUT_DIR" -type d \( -name .git \) -prune -o -type f -print | sort | while read -r FILE; do
  # Use the raw path as given by find (absolute or relative)
  echo "\`$FILE\`:" >> "$OUTPUT_FILE"
  echo '```'             >> "$OUTPUT_FILE"
  cat "$FILE"            >> "$OUTPUT_FILE"
  echo                   >> "$OUTPUT_FILE"
  echo '```'             >> "$OUTPUT_FILE"
  echo                   >> "$OUTPUT_FILE"
done
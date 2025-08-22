#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Script Name: read_files_and_content.sh
#
# Description:
#   This script collects all files under a specified input directory (excluding
#   any `.git` folders and their contents) and concatenates them, in
#   deterministic sorted order, into a single output file.
#
# Usage:
#   ./read_files_and_content.sh <input_directory> <output_file>
#
# Arguments:
#   <input_directory>  Path to the directory to search files in.
#   <output_file>      Path to the file where concatenated content is written.
#
# Example:
#   ./read_files_and_content.sh "./src" "collected.md"
#
# Notes:
#   - Overwrites <output_file> if it already exists.
#   - Ensures deterministic order by sorting file paths.
#   - Skips `.git` directories and everything inside them.
# -----------------------------------------------------------------------------

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
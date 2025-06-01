#!/bin/bash

# Do the following before running this script:
# 1. Install Poetry (https://python-poetry.org/docs/#installation)
# 2. Give permission to execute this script: chmod +x run_tests_data_health.sh

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Save the current PYTHONPATH to restore it later
ORIGINAL_PYTHONPATH="$PYTHONPATH"

# Navigate to the tests directory
cd "$SCRIPT_DIR"

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo "Creating pyproject.toml in the tests directory..."
    # Initialize a new Poetry project in the tests directory
    poetry init -n --name "tests"
fi

# Path to the requirements.txt file for health data
REQUIREMENTS_FILE="$SCRIPT_DIR/../src/data_acquisition/health/requirements.txt"

# Check if requirements.txt exists
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Checking for new dependencies in requirements.txt..."

    # Read each dependency from requirements.txt
    while read -r dependency; do
        # Skip empty lines and comments
        if [[ -z "$dependency" || "$dependency" == \#* ]]; then
            continue
        fi

        # Extract the package name (handles version specifiers)
        package_name=$(echo "$dependency" | cut -d '=' -f 1 | cut -d '<' -f 1 | cut -d '>' -f 1 | cut -d '~' -f 1 | tr -d ' ')

        # Check if dependency is already in pyproject.toml
        if ! poetry show "$package_name" &> /dev/null; then
            echo "Adding dependency: $dependency"
            poetry add "$dependency"
        else
            echo "Dependency '$package_name' is already satisfied."
        fi
    done < "$REQUIREMENTS_FILE"
else
    echo "Requirements file not found at $REQUIREMENTS_FILE"
    exit 1
fi

# Set PYTHONPATH to include the root directory
export PYTHONPATH="$SCRIPT_DIR/..":$PYTHONPATH

# Run the tests using unittest
echo "Running health data tests..."

poetry run python -m unittest discover -s "$SCRIPT_DIR/test_data_acquisition/test_health" -p "*.py"

# Restore the original PYTHONPATH
export PYTHONPATH="$ORIGINAL_PYTHONPATH"

echo "Test run complete. Exited."

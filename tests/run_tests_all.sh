#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the tests directory
cd "$SCRIPT_DIR"

# Give permission to execute air_quality.
chmod +x ./run_tests_data_air_quality.sh

# Run the tests.
echo "Running tests for data air_quality..."
./run_tests_data_air_quality.sh

# Give permission to execute health.
chmod +x ./run_tests_data_health.sh

# Run the tests.
echo "Running tests for data health..."
./run_tests_data_health.sh
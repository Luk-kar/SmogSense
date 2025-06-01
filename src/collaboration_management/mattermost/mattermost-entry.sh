#!/bin/bash

set -m

# Construct the datasource URL
export MM_SQLSETTINGS_DATASOURCE="postgres://${MM_USERNAME}:${MM_PASSWORD}@postgres:5432/mattermost?sslmode=disable&connect_timeout=10"

# Start Mattermost in the background
echo "Starting Mattermost..."
/mattermost/bin/mattermost &

# Wait for Mattermost to start
until curl --silent --fail http://localhost:8065/api/v4/system/ping; do
  echo "Waiting for Mattermost to start..."
  sleep 5
done

echo "Mattermost has started."

# Wait for the Boards plugin to be available
until /mattermost/bin/mmctl --local plugin list | grep 'focalboard'; do
  echo "Waiting for the Boards plugin to be installed..."
  sleep 5
done

# Enable the Boards plugin
echo "Enabling the Boards plugin..."
/mattermost/bin/mmctl --local plugin enable focalboard

# Bring Mattermost to the foreground
echo "Mattermost is ready to use!"
fg %1

#!/bin/sh

echo "Starting Apache Superset"
echo "------------------------"
echo "username:  ${SUPERSET_ADMIN_USERNAME}"
echo "firstname: ${SUPERSET_ADMIN_FIRST_NAME}"
echo "lastname:  ${SUPERSET_ADMIN_LAST_NAME}"
echo "email:     ${SUPERSET_ADMIN_EMAIL}"
echo "port:      ${SUPERSET_HOST_PORT}"
echo "------------------------"

# Initialize Superset database
superset db upgrade

# Export Flask application
export FLASK_APP=superset

# Create an admin user (you can modify the username, email, and password as needed)
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USERNAME}" \
    --firstname "${SUPERSET_ADMIN_FIRST_NAME}" \
    --lastname "${SUPERSET_ADMIN_LAST_NAME}" \
    --email "${SUPERSET_ADMIN_EMAIL}" \
    --password "${SUPERSET_ADMIN_PASSWORD}"

# Initialize Superset
superset init

# Add the PostgreSQL data source
superset set-database-uri \
    --database_name warehouse_db \
    --uri "postgresql://${SUPERSET_DB_USER}:${SUPERSET_DB_PASSWORD}@${SUPERSET_DB_HOST}:${SUPERSET_DB_PORT}/${POSTGRES_WAREHOUSE_DB}"

# TODO: You can upload these in the UI from src/analytics/superset/dashboards, for now uploading dashboards by CLI is broken
# Echo all dashboard ZIP files in the mounted directory
# echo "Found the following dashboard ZIP files in /tmp/superset/dashboards/:"
# for file in /tmp/superset/dashboards/*.zip; do
#     echo " - $file"
# done

# # Import each dashboard ZIP file using the admin username
# for file in /tmp/superset/dashboards/*.zip; do
#     echo "Importing dashboards from $file"
#     superset import-dashboards -p "$file" --username "${SUPERSET_ADMIN_USERNAME}"
# done

echo "Remember to provide the correct password for the POSTGRES_WAREHOUSE_DB connection in the Superset UI."


# Start the Superset server
superset run -h 0.0.0.0 -p "${SUPERSET_HOST_PORT}" --with-threads --reload --debugger

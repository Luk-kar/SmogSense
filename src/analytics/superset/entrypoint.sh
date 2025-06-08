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

# BUG: superset.commands.exceptions.CommandInvalidError: Error importing dashboard, do via ansible instead
# # Import dashboards from ZIP files
# echo "Looking for dashboard ZIP files in /tmp/superset/dashboards/..."
# for file in /tmp/superset/dashboards/*.zip; do
#     if [ -e "$file" ]; then
#         echo "Importing dashboards from $file"
#         superset import-dashboards -u "${SUPERSET_ADMIN_USERNAME}" -p "$file"
#     else
#         echo "No dashboard ZIP files found in /tmp/superset/dashboards/"
#         break
#     fi
# done

echo "Remember to provide the correct password for the POSTGRES_WAREHOUSE_DB connection in the Superset UI."

mkdir -p /app/pythonpath
# Create superset_config.py with PUBLIC_ROLE_LIKE setting
cat <<EOF > /app/pythonpath/superset_config.py
PUBLIC_ROLE_LIKE = "Gamma"
EOF
echo "Created /app/pythonpath/superset_config.py with PUBLIC_ROLE_LIKE = 'Gamma'"
echo "Exposed public role for anonymous access to dashboards."

# Start the Superset server
superset run -h 0.0.0.0 -p "${SUPERSET_HOST_PORT}" --with-threads --reload --debugger

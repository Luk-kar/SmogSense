#!/usr/bin/env bash
set -e

echo "Starting database creation process."

# Create the additional databases
echo "Creating database ${MLFLOW_DB_NAME:-mlflow} with owner ${MLFLOW_DB_USERNAME:-$POSTGRES_USER}:"
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${MLFLOW_DB_NAME:-mlflow}
        WITH OWNER = ${MLFLOW_DB_USERNAME:-$POSTGRES_USER}
        ENCODING = 'UTF8'
        CONNECTION LIMIT = -1;
EOSQL

echo "Creating database ${POSTGRES_WAREHOUSE_DB:-smogsense} with owner ${POSTGRES_USER}:"
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${POSTGRES_WAREHOUSE_DB:-smogsense}
        WITH OWNER = ${POSTGRES_USER}
        ENCODING = 'UTF8'
        CONNECTION LIMIT = -1;
EOSQL

echo "Creating database ${DAGSTER_PG_DB:-dagster} with owner ${DAGSTER_PG_USERNAME:-$POSTGRES_USER}:"
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${DAGSTER_PG_DB:-dagster}
        WITH OWNER = ${DAGSTER_PG_USERNAME:-$POSTGRES_USER}
        ENCODING = 'UTF8'
        CONNECTION LIMIT = -1;
EOSQL

echo "Creating database ${MM_DBNAME:-mattermost} with owner ${MM_USERNAME:-$POSTGRES_USER}:"
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ${MM_DBNAME:-mattermost}
        WITH OWNER = ${MM_USERNAME:-$POSTGRES_USER}
        ENCODING = 'UTF8'
        CONNECTION LIMIT = -1;
EOSQL

# Enable the PostGIS extension
echo "Enabling PostGIS extension for database ${POSTGRES_WAREHOUSE_DB:-smogsense}:"
psql --username "$POSTGRES_USER" --dbname "${POSTGRES_WAREHOUSE_DB:-smogsense}" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    SELECT postgis_full_version();
EOSQL

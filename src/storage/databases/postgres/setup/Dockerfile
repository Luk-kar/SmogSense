FROM postgres:15.8

# Install PostGIS and the associated PostgreSQL extension
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgis \
    postgresql-15-postgis-3 && \
    rm -rf /var/lib/apt/lists/*

# By default, the postgres image will run any scripts in /docker-entrypoint-initdb.d
# to initialize the database. We can add a script here to enable PostGIS automatically.
COPY init-dbs.sh /docker-entrypoint-initdb.d/

# Ensure the init script is executable
RUN chmod +x /docker-entrypoint-initdb.d/init-dbs.sh

"""
This module provides utility functions for performing schema and table operations
in a database using SQLAlchemy and Dagster.
"""

# Dagster
from dagster import (
    AssetExecutionContext,
    Failure,
)

# SQLAlchemy
from sqlalchemy import (
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.schema import Table

# .database
from common.utils.database.session_handling import get_database_session


def remove_schema_with_cascade(context: AssetExecutionContext, SCHEMA_NAME: str):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """

    with get_database_session(context) as session:

        drop_statement = text(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE")

        session.execute(drop_statement)

        context.log.info(f"Dropped schema '{SCHEMA_NAME}' with CASCADE.")


def ensure_schema_exists(
    engine: Engine, schema_name: str, context: AssetExecutionContext
):
    """Ensure the schema exists in the database."""
    with engine.connect() as connection:
        if not engine.dialect.has_schema(connection, schema_name):
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            connection.commit()
            context.log.info(f"Created schema '{schema_name}'.")


def ensure_table_exists(engine: Engine, table: Table, context: AssetExecutionContext):
    """Ensure the table exists within the schema."""

    table_name = table.name
    schema_name = table.schema

    log_table_columns(table, context)

    with engine.connect() as connection:
        if not engine.dialect.has_table(connection, table_name, schema=schema_name):

            table.create(bind=engine)
            context.log.info(f"Created table '{table_name}' in schema '{schema_name}'.")
        else:
            context.log.info(
                f"Table '{table_name}' already exists in schema '{schema_name}'."
            )


def log_table_columns(table: Table, context: AssetExecutionContext):
    """Log the names and types columns of a table."""

    table_name = table.name
    columns = table.columns
    columns_str = "\n".join([f"{col.name}: {col.type}" for col in columns])
    context.log.info(f"Table '{table_name}' columns:\n{columns_str}")


def drop_user_schemas(context: AssetExecutionContext, engine: Engine):
    """
    Drop all user schemas except the default ones.
    """

    context.log.info("Dropping all user schemas...")

    with engine.connect() as conn:
        # Get list of non-system schemas
        schemas = (
            conn.execute(
                text(
                    """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT LIKE 'pg_%'
                AND schema_name NOT IN ('information_schema', 'public');
            """
                )
            )
            .scalars()
            .all()
        )

    if schemas:
        context.log.info(f"➡️ Dropping schemas: {schemas}")
        with engine.begin() as conn:  # Transaction block for dropping schemas
            for schema in schemas:
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        context.log.info("✅ Schemas dropped successfully.")
    else:
        context.log.info("➡️ No user schemas to drop.")

    # Check if any schema exists
    with engine.connect() as conn:
        schema_exists = conn.execute(
            text(
                """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.schemata
                WHERE schema_name NOT LIKE 'pg_%'
                AND schema_name NOT IN ('information_schema', 'public')
            )
            """
            )
        ).scalar()

    if schema_exists:
        context.log.error("❌ User schemas still exist after dropping.")
        raise Failure("User schemas still exist after dropping.")
    else:
        context.log.info("✅ All user schemas dropped successfully.")


def drop_public_tables(context: AssetExecutionContext, engine: Engine):
    """
    Drop all public tables, views, and materialized views.
    """

    context.log.info("Dropping all public tables...")

    with engine.connect() as conn:

        # Drop all public tables, views, and materialized views
        conn.execute(
            text(
                """
                DO $$ 
                DECLARE 
                    r RECORD;
                BEGIN
                    -- Drop Materialized Views
                    FOR r IN (SELECT matviewname FROM pg_matviews WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS public.' || quote_ident(r.matviewname) || ' CASCADE;';
                    END LOOP;
                    -- Drop Views (EXCLUDING PostGIS views)
                    FOR r IN (
                        SELECT table_name 
                        FROM information_schema.views 
                        WHERE table_schema = 'public'
                        AND table_name NOT IN (
                            'geography_columns', 
                            'geometry_columns', 
                            'raster_columns', 
                            'raster_overviews'
                        )
                    ) LOOP
                        EXECUTE 'DROP VIEW IF EXISTS public.' || quote_ident(r.table_name) || ' CASCADE;';
                    END LOOP;
                    -- Drop Tables
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public'
                    AND tablename NOT IN ('spatial_ref_sys')) LOOP
                        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE;';
                    END LOOP;
                END $$;
                """
            )
        )

        # Check if there are tables
        tables_exist = conn.execute(
            text(
                """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name NOT IN (
                    'spatial_ref_sys', 
                    'geography_columns', 
                    'geometry_columns', 
                    'raster_columns', 
                    'raster_overviews'
                )
            )
            """
            )
        ).scalar()

    if tables_exist:
        context.log.error("❌ Public tables still exist after dropping.")
        raise Failure("Public tables still exist after dropping.")
    else:
        context.log.info("✅ All public tables dropped successfully")


def create_public_schema_if_not_exists(context: AssetExecutionContext, engine: Engine):
    """Ensure the public schema exists in the database."""

    with engine.connect() as connection:

        connection.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        connection.commit()
        context.log.info("Ensured public schema exists.")


def get_table_name(model: DeclarativeMeta) -> str:
    """
    Returns the fully qualified table name for a given SQLAlchemy model.
    """

    table = model.__table__
    schema = table.schema
    name = table.name

    if schema:
        return f"{schema}.{name}"
    return name

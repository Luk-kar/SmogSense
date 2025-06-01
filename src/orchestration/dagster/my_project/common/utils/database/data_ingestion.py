"""
This module provides utility functions for uploading data to a PostgreSQL database
using SQLAlchemy and Pandas DataFrames. It includes functions for performing bulk
inserts, upserts, and copying data, with support for handling unique constraints
and primary key conflicts.
"""

# Python
from typing import Any, Type, Literal
import io

# Third-party
import pandas as pd
from psycopg2 import sql

# Dagster
from dagster import (
    AssetExecutionContext,
    Failure,
)

# SQLAlchemy
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session

# Pipeline
from common.utils.ORM import (
    get_primary_key_columns,
    get_unique_constraint_columns,
)
from common.utils.logging import (
    log_asset_materialization,
)

# .database
from common.utils.database.schema_operations import (
    ensure_schema_exists,
    ensure_table_exists,
)


def upload_data_asset(
    context: AssetExecutionContext,
    data_frame: pd.DataFrame,
    model_class: Type[DeclarativeMeta],
    mode: Literal["copy", "update_non_id_values"] = None,
):
    """
    Insert new records, preserving historical data
    by skipping duplicates on unique constraints.
    If copy is True, the data is copied to a new table.
    Coping is useful when you are assured that
    the data is not updated too often and it is huge in size.
    """

    if mode and mode not in ["copy", "update_non_id_values"]:
        raise ValueError(f"Invalid mode: {mode}")

    engine = context.resources.postgres_alchemy
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    table_name = model_class.__tablename__
    table = model_class.__table__
    schema_name = table.schema

    try:
        # Ensure schema and table exist
        ensure_schema_exists(engine, schema_name, context)
        ensure_table_exists(engine, table, context)

        context.log.info(f"{table_name}: rows {len(data_frame)}")
        context.log.info(f"Columns: {data_frame.columns.tolist()}")
        context.log.info(f"Data types:\n{data_frame.dtypes}")
        context.log.info(f"Table path: {schema_name}.{table_name}")
        context.log.info("Uploading the data to PostgreSQL.")

        # Convert DataFrame to list of dictionaries
        records = data_frame.to_dict(orient="records")

        # Check for autoincrement on the primary key
        if mode == "copy":

            context.log.info(f"Copying data to a new table for {table_name}.")

            bulk_copy_data(
                engine,
                model_class,
                data_frame,
                context,
            )

        elif mode == "update_non_id_values":

            context.log.info(
                "Performing bulk insert with optional values update"
                f"for already existing ids in {table_name} data."
            )

            perform_bulk_insert_with_update_of_non_id_values(
                session,
                model_class,
                records,
                context=context,
            )

        elif any(col.autoincrement for col in table.columns if col.primary_key):
            # Use bulk insert with unique constraint skip

            context.log.info(
                f"Performing bulk insert with unique constraint for {table_name} data."
            )

            perform_bulk_insert_with_autoincrement(
                session,
                model_class,
                records,
                context=context,
            )
        else:
            # Perform bulk upsert if no autoincrement is set on the primary key

            context.log.info(f"Performing bulk upsert for {table_name} data.")

            perform_bulk_upsert(
                session,
                model_class,
                records,
                context=context,
            )

    except SQLAlchemyError as e:
        session.rollback()
        context.log.error(f"Error uploading {table_name} data: {e}")
        raise Failure(f"Failed to upload {table_name} data: {e}") from e
    finally:
        session.close()


def perform_bulk_upsert(
    session: Session,
    model_class: Type[DeclarativeMeta],
    records: list[dict[str, Any]],
    context: AssetExecutionContext,
):
    """Perform a bulk upsert operation with conflict resolution."""

    table = model_class.__table__

    primary_key_columns = get_primary_key_columns(model_class)
    unique_constraint_columns = get_unique_constraint_columns(model_class)

    # Prepare bulk upsert statement with conflict handling
    insert_statement = insert(table).values(records)

    # Prepare the dictionary of updates for the upsert operation
    update_values = get_conflict_update_values(
        insert_statement.excluded, primary_key_columns
    )

    # Construct the 'ON CONFLICT' clause to handle duplicate key conflicts
    bulk_upsert_statement = insert_statement.on_conflict_do_update(
        index_elements=unique_constraint_columns, set_=update_values
    )

    context.log.info("Uploading data to PostgreSQL...")

    # Execute the statement
    session.execute(bulk_upsert_statement)
    session.commit()
    context.log.info(
        f"Uploaded {len(records)} records to '{table.name}' using bulk upsert."
    )


def perform_bulk_insert_with_autoincrement(
    session: Session,
    model_class: Type[DeclarativeMeta],
    records: list[dict[str, Any]],
    context: AssetExecutionContext,
):
    """Perform a bulk insert operation, ignoring conflicts based on unique constraints."""

    table = model_class.__table__
    primary_key_columns = get_primary_key_columns(model_class)

    # Delete column with primary key if it exists
    records = [
        {
            key: value
            for key, value in record.items()
            if (key not in primary_key_columns)
        }
        for record in records
    ]

    # log deleted columns
    context.log.info("columns without primary key:" f"\n{set(records[0])}")

    # Prepare bulk insert statement with conflict handling
    bulk_insert_statement = (
        insert(table).values(records).values(records).on_conflict_do_nothing()
    )

    context.log.info("Uploading data to PostgreSQL...")

    # Execute the statement
    session.execute(bulk_insert_statement)
    session.commit()
    context.log.info(
        f"Inserted {len(records)} records into '{table.name}', ignoring conflicts."
    )


def perform_bulk_insert_with_update_of_non_id_values(
    session: Session,
    model_class: Type[DeclarativeMeta],
    records: list[dict[str, Any]],
    context: AssetExecutionContext,
):
    """Perform a bulk insert operation, ignoring conflicts based on ids."""

    table = model_class.__table__
    primary_key_columns = get_primary_key_columns(
        model_class
    )  # e.g. ["id"] or ["id_tweet"]

    # Log which columns appear in the first record
    context.log.info(f"Columns in the first record:\n{set(records[0].keys())}")

    # 1) Create the INSERT statement with all columns present
    insert_stmt = insert(table).values(records)

    # 2) Exclude primary-key columns from the update set
    #    This ensures PK columns are used to match existing rows
    #    but never overwritten.
    update_values = {
        col.name: col
        for col in insert_stmt.excluded
        if col.name not in primary_key_columns
    }

    # 3) Configure the ON CONFLICT clause to do an UPDATE of non-PK columns
    conflict_stmt = insert_stmt.on_conflict_do_update(
        index_elements=primary_key_columns,  # match on these columns
        set_=update_values,  # update only the other columns
    )

    context.log.info(
        f"Performing bulk insert with update of non-id values for '{table.name}'."
    )

    # 4) Execute and commit
    session.execute(conflict_stmt)
    session.commit()

    context.log.info(f"Inserted/updated {len(records)} records in '{table.name}'.")


def bulk_copy_data(
    engine,
    model_class: Type[DeclarativeMeta],
    data_frame: pd.DataFrame,
    context: AssetExecutionContext,
):
    """
    Bulk copy data from a DataFrame to a PostgreSQL table using the COPY command.
    """

    # Convert DataFrame to CSV format in memory
    csv_data = data_frame.to_csv(index=False, header=False, sep="\t", na_rep="\\N")

    context.log.info("First 3 rows of the csv to upload:")
    context.log.info(csv_data[: csv_data.find("\n") * 3])

    table_name = model_class.__tablename__
    schema_name = model_class.__table__.schema

    # Establish a raw connection
    connection = engine.raw_connection()
    cursor = connection.cursor()

    # Use COPY command to bulk load data
    try:
        # Prepare column identifiers
        columns = [sql.Identifier(col) for col in data_frame.columns]

        # Construct the COPY command using psycopg2.sql module
        copy_sql = sql.SQL(
            """
            COPY {schema_table} ({columns})
            FROM STDIN WITH (
                FORMAT CSV,
                DELIMITER E'\t',
                NULL '\\N'
            )
        """
        ).format(
            schema_table=sql.Identifier(schema_name, table_name),
            columns=sql.SQL(", ").join(columns),
        )

        cursor.copy_expert(copy_sql, io.StringIO(csv_data))

        connection.commit()

        context.log.info(f"Bulk copied data into '{table_name}'.")

    except Exception as e:

        connection.rollback()
        raise Failure(f"Failed to bulk copy data into '{table_name}': {e}") from e

    finally:
        cursor.close()
        connection.close()


def get_conflict_update_values(excluded_columns, columns_to_skip) -> dict[str, Any]:
    """Generate a dictionary of column updates for conflict handling."""
    return {
        column_metadata.name: column_metadata
        for column_metadata in excluded_columns
        if column_metadata.name not in columns_to_skip
    }


def upload_data_and_log_materialization(
    context: AssetExecutionContext,
    data_frame: pd.DataFrame,
    model_class,
    asset_key_str: str,
    description: str,
    mode: Literal["copy", "update_non_id_values"] = None,
):
    """Uploads data to the database and logs an AssetMaterialization event."""
    upload_data_asset(
        context=context,
        data_frame=data_frame,
        model_class=model_class,
        mode=mode,
    )

    log_asset_materialization(
        context=context,
        asset_key=asset_key_str,
        data_frame=data_frame,
        description=description,
    )

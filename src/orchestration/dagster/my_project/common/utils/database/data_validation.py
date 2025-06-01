"""
This module provides utility functions for data validation between uploaded
Pandas DataFrames and database tables using SQLAlchemy ORM models. It includes
functions to compare data, check for mismatches in row counts, columns, and
data types, and load data from a database table into a DataFrame.
"""

# Python
from dataclasses import dataclass
from typing import Any, Type, Set

# Third-party
import pandas as pd

# For handling geometry columns (PostGIS)
from geoalchemy2 import Geometry

# Dagster
from dagster import (
    AssetCheckExecutionContext,
    AssetCheckResult,
    Failure,
)

# SQLAlchemy
from sqlalchemy import (
    Integer,
    BigInteger,
    SmallInteger,
    String,
    Float,
    Numeric,
    Date,
    DateTime,
    Boolean,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta


def compare_uploaded_database_data(
    context: AssetCheckExecutionContext,
    df_uploaded: pd.DataFrame,
    model_class: Type[DeclarativeMeta],
) -> AssetCheckResult:
    """
    Compare the uploaded DataFrame with the data in the database.
    """

    engine = context.resources.postgres_alchemy
    table_name = model_class.__tablename__

    try:
        # Fetch data from the database
        df_database = load_database_table(engine, model_class)

        # Compare DataFrames
        result = compare_dataframes(df_database, df_uploaded, model_class)

        return result

    except Exception as e:
        context.log.error(f"Error checking '{table_name}' data: {e}")
        raise Failure(f"Failed to check '{table_name}' data: {e}") from e


@dataclass
class ValidationResult:
    """
    Data class to store the result of data validation checks.
    """

    passed: bool = True
    metadata: dict = None
    database_columns: Set[str] = None
    orm_columns: Set[str] = None

    def __post_init__(self):
        self.metadata = self.metadata or {}


def compare_dataframes(
    df_database: pd.DataFrame,
    df_uploaded: pd.DataFrame,
    model_class: Type[DeclarativeMeta],
) -> AssetCheckResult:
    """Compare uploaded DataFrame with database data using ORM model."""
    result = ValidationResult()

    _validate_row_count(df_database, df_uploaded, result)
    _validate_column_match(df_database, df_uploaded, model_class, result)
    _validate_data_types(df_database, model_class, result)

    return AssetCheckResult(
        passed=result.passed,
        metadata=result.metadata,
    )


def _validate_row_count(
    df_db: pd.DataFrame, df_upload: pd.DataFrame, result: ValidationResult
) -> None:
    """Validate row counts between database and uploaded data."""
    db_count = len(df_db)
    upload_count = len(df_upload)

    if db_count < upload_count:
        result.passed = False
        result.metadata["Row count mismatch"] = (
            f"DB: {db_count}, Upload: {upload_count}"
        )
    else:
        result.metadata["Row count"] = db_count


def _validate_column_match(
    df_db: pd.DataFrame,
    df_upload: pd.DataFrame,
    model: Type[DeclarativeMeta],
    result: ValidationResult,
) -> None:
    """Validate column consistency between ORM, DB, and upload."""
    db_cols = set(df_db.columns)
    orm_cols = set(model.__table__.columns.keys())
    result.database_columns = db_cols
    result.orm_columns = orm_cols

    if db_cols != orm_cols:
        result.passed = False
        result.metadata["Column mismatch"] = {"ORM": orm_cols, "Database": db_cols}

    result.metadata.update(
        {
            "Database columns": list(db_cols),
            "Upload columns": list(df_upload.columns),
            "ORM columns": list(orm_cols),
        }
    )


def _validate_data_types(
    df_db: pd.DataFrame, model: Type[DeclarativeMeta], result: ValidationResult
) -> None:
    """Validate data types between database and ORM model."""
    if not result.database_columns or not result.orm_columns:
        return

    common_cols = result.database_columns & result.orm_columns
    mismatches = {}

    for col in common_cols:
        orm_type = map_sqlalchemy_type_to_pandas_dtype(
            model.__table__.columns[col].type
        )
        db_type = str(df_db[col].dtype).lower()

        if db_type != orm_type:
            result.passed = False
            mismatches[col] = f"ORM: {orm_type}, DB: {db_type}"

    if mismatches:
        result.metadata["Data type mismatches"] = mismatches
    else:
        result.metadata["Data types"] = {
            col: str(df_db[col].dtype) for col in common_cols
        }


def load_database_table(
    engine: Engine, model_class: Type[DeclarativeMeta]
) -> pd.DataFrame:
    """
    Load data from a database table into a DataFrame.
    """

    schema_name = model_class.__table__.schema

    df_db = pd.read_sql_table(
        table_name=model_class.__tablename__,
        con=engine,
        schema=schema_name,
    )

    df_db = convert_columns_to_appropriate_dtypes(df_db)

    return df_db


def convert_columns_to_appropriate_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame columns to appropriate data types.
    """
    for col in df.columns:

        # int64 with nulls is converted to float64 in Pandas
        if df[col].dtype == "float64" and df[col].isnull().any():

            try:
                df[col] = df[col].astype("Int64")  # Pandas nullable integer
            except TypeError:
                # If conversion fails, keep as float64
                pass

    return df


def map_sqlalchemy_type_to_pandas_dtype(sqlalchemy_type: Any) -> str:
    """
    Map a given SQLAlchemy column type to its corresponding Pandas dtype.

    1. If the type is TIMESTAMP, check for timezone=True or False and look up
       (TIMESTAMP, tz_flag) in the dict.
    2. Otherwise, search for a single-type key that matches (via isinstance).
    3. Fallback to returning the string representation if no match is found.
    """

    _SQLALCHEMY_TO_PANDAS = {
        (TIMESTAMP, True): "datetime64[ns, utc]",  # TIMESTAMP WITH TIME ZONE
        (TIMESTAMP, False): "datetime64[ns]",  # TIMESTAMP WITHOUT TIME ZONE
        Integer: "int64",
        BigInteger: "int64",
        SmallInteger: "int64",
        Float: "float64",
        Numeric: "float64",
        String: "object",  # Pandas 'object' dtype for generic strings
        Date: "datetime64[ns]",
        DateTime: "datetime64[ns]",
        Boolean: "bool",
        Geometry: "object",  # Pandas 'object' dtype for geometry columns
    }

    for key, pandas_dtype in _SQLALCHEMY_TO_PANDAS.items():

        if isinstance(key, tuple):

            # 1) Handle TIMESTAMP type with timezone attribute
            if isinstance(sqlalchemy_type, key[0]):
                tz_flag = getattr(sqlalchemy_type, "timezone", False)
                if tz_flag == key[1]:
                    return pandas_dtype
        else:

            # 2) Handle all other non-tuple types
            if isinstance(sqlalchemy_type, key):
                return pandas_dtype

    # 3) Fallback: return the string representation if no match is found
    return str(sqlalchemy_type).lower()

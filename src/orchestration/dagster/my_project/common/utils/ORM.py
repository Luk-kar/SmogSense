"""
Utilities for working with SQLAlchemy ORM classes.
"""

# Python
from typing import Type
from functools import reduce

# Third-party
import pandas as pd

# SQLAlchemy
from sqlalchemy import (
    Index,
    UniqueConstraint,
    String,
)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.inspection import inspect

Base = declarative_base()

# validation utilities


def get_model_non_primary_keys_and_non_generated_columns(
    model_class: Type[DeclarativeMeta],
) -> list:
    """
    Get the column names of a SQLAlchemy model class.
    """
    return [
        column.name
        for column in model_class.__table__.columns
        if not (column.primary_key and column.autoincrement)
    ]


def get_unique_constraint_columns(model_class: Type[DeclarativeMeta]) -> list[str]:
    """Return a list of unique constraint column names for the given SQLAlchemy model class."""

    unique_constraints = set()

    for table_arg in model_class.__table_args__:
        if isinstance(table_arg, (UniqueConstraint, Index)):

            for column in table_arg.columns:
                unique_constraints.add(column.name)

    return list(unique_constraints)


def get_primary_key_columns(model_class: Type[DeclarativeMeta]) -> list[str]:
    """Return a list of primary key column names for the given SQLAlchemy model class."""
    return [
        column.name for column in model_class.__table__.columns if column.primary_key
    ]


def get_columns_to_check(orm_class: DeclarativeMeta) -> list[str]:
    """
    Generate a dictionary of column names and their nullable status based on the ORM class.

    Args:
        orm_class (DeclarativeMeta): SQLAlchemy ORM class.

    Returns:
        dict: Dictionary with column names as keys and nullable status as values.
    """
    columns_to_check = []
    mapper = inspect(orm_class)

    for column in mapper.columns:

        # Consider String columns only and add constraints for emptiness
        if isinstance(column.type, String):
            columns_to_check.append(column.name)

    return columns_to_check


def find_invalid_rows(df: pd.DataFrame, metadata_class: Type[Base]) -> pd.DataFrame:
    """
    Finds rows in a DataFrame that violate the constraint of non-empty string values.

    Args:
        df (pd.DataFrame): The DataFrame to check.
        columns_to_check (dict): Dictionary where keys are column names, and values are booleans.
                                 A boolean `True` indicates the column is nullable (e.g., "street_address").

    Returns:
        pd.DataFrame: DataFrame containing invalid rows.
    """

    columns_to_check = get_columns_to_check(metadata_class)

    conditions = []

    for column in columns_to_check:

        conditions.append(df[column].notna() & (df[column].str.strip() == ""))

    # Combine all conditions using logical OR
    combined_condition = reduce(
        lambda current_condition, next_condition: current_condition | next_condition,
        conditions,
    )

    # Return rows that satisfy any of the invalid conditions
    return df[combined_condition]

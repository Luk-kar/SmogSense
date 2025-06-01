"""
Utility functions for working with DataFrames in Dagster assets.
"""

# Python
from typing import Type

# Third-party
import pandas as pd

# Dagster
from dagster import AssetExecutionContext, AssetCheckResult, Failure

# SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy import (
    Float,
    Integer,
    String,
    BigInteger,
)

# Common
from common.utils.logging import log_dataframe_info

Base = declarative_base()


def ensure_dataframe_columns_match_model(
    df: pd.DataFrame, model_class: Type[DeclarativeMeta]
):
    """
    Validate if DataFrame columns match the model class columns.
    Raises an error if DataFrame columns do not match model class columns.
    """

    # Get columns from the model class
    model_columns = set(
        [
            column.name
            for column in model_class.__table__.columns
            if not (column.primary_key and column.autoincrement)
        ]
    )
    df_columns = set(df.columns)

    # Check if DataFrame columns match model class columns
    if df_columns != model_columns:

        missing_in_df = model_columns - df_columns
        extra_in_df = df_columns - model_columns

        out_of_order = [
            (df_col, model_col)
            for df_col, model_col in zip(df_columns, model_columns)
            if df_col != model_col
        ]

        raise ValueError(
            f"Column mismatch for {model_class.__name__}: "
            f"Missing in DataFrame: {missing_in_df}. "
            f"Extra in DataFrame: {extra_in_df}."
            f"Out of order: {out_of_order}."
        )


def replace_greek_mu_with_micro_character(name: str) -> str:
    """
    Replace the Greek letter 'µ' with the micro character 'μ'.
    """
    return name.replace("µ", "μ")


def convert_to_dataframe(
    context: AssetExecutionContext, flattened_data: list
) -> pd.DataFrame:
    """
    Convert the flattened data to a DataFrame.
    """
    try:
        df = pd.DataFrame(flattened_data)

        log_dataframe_info(context, df, "Flattened data")

        # Count nulls in columns with nulls
        null_counts = df.isnull().sum()
        null_columns = null_counts[null_counts > 0]

        if not null_columns.empty:
            for col, count in null_columns.items():
                context.log.info(f"➡️ Column '{col}' has {count} null values.")

            rows_with_nulls = df[df.isnull().any(axis=1)]
            num_rows_with_nulls = len(rows_with_nulls)

            if num_rows_with_nulls > 0:
                context.log.info(
                    f"➡️ Number of rows with null values:\n{num_rows_with_nulls}"
                )
                context.log.info(
                    f"➡️ Sample rows with null values:\n{rows_with_nulls.head(3)}"
                )

        else:
            context.log.info("✅ No null values found in the data.")

    except Exception as e:
        context.log.error(f"❌ Error converting data to DataFrame:\n{e}")
        raise Failure(f"Failed to convert data to DataFrame:\n{e}") from e
    return df


def drop_rows_with_nulls(
    df: pd.DataFrame, model_class: Type[DeclarativeMeta]
) -> pd.DataFrame:
    """
    Drop rows from DataFrame have null values in the non-nullable columns, in the model class.
    Raises an error if DataFrame columns do not match model class columns.
    """

    # Identify non-nullable columns in the model class that are present in the DataFrame
    non_nullable_columns = [
        column.name
        for column in model_class.__table__.columns
        if not column.nullable and column.name in df.columns
    ]

    # Drop rows with nulls in non-nullable columns
    return df.dropna(subset=non_nullable_columns)


def reorder_dataframe_columns(
    df: pd.DataFrame, model_class: Type[Base]
) -> pd.DataFrame:
    """
    Reorder the DataFrame columns to match the order in the SQLAlchemy model class,
    using the column names as defined in the database (i.e., the 'name' attribute).
    """
    # Extract column names in the model's defined order, using column.name
    model_columns = [column.name for column in inspect(model_class).columns]
    return df[model_columns]


def apply_default_ordering(
    df: pd.DataFrame, model_class: type, context: AssetExecutionContext
) -> pd.DataFrame:
    """
    Sort a DataFrame based on the __default_order_by__ attribute of a SQLAlchemy model.

    Parameters:
        df (pd.DataFrame): The DataFrame to be sorted.
        model_class (type): The SQLAlchemy model class with __default_order_by__ attribute.

    Returns:
        pd.DataFrame: The sorted DataFrame.
    """

    if (
        not hasattr(model_class, "__default_order_by__")
        or not model_class.__default_order_by__
    ):
        context.log.warning(
            f"No default ordering specified for {model_class.__name__}. Data will not be sorted."
        )
        return df

    context.log.info(
        f"Applying default ordering for {model_class.__name__}: {model_class.__default_order_by__}"
    )

    sort_columns = []
    order_direction = []

    for column, order in model_class.__default_order_by__.items():

        sort_columns.append(column)

        if order.lower() in ["asc", "ascending"]:
            order_direction.append(True)
        elif order.lower() in ["desc", "descending"]:
            order_direction.append(False)
        else:
            raise ValueError(f"Invalid order direction '{order}' for column '{column}'")

    return df.sort_values(by=sort_columns, ascending=order_direction)


def check_dataframe_structure(
    df: pd.DataFrame,
    model_class: Type[DeclarativeMeta],
) -> AssetCheckResult:
    """
    Validates the structure of a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to validate.
        model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.

    Returns:
        AssetCheckResult: The result of the validation check.
    """

    expected_columns = generate_expected_columns(model_class)

    passed = True
    metadata = {
        "Total rows": len(df),
        "Columns": list(df.columns),
        "Expected columns": list(expected_columns.keys()),
        "Data types": {col: str(dtype).lower() for col, dtype in df.dtypes.items()},
    }

    # Check number of columns
    if set(df.columns) != set(expected_columns.keys()):
        passed = False
        metadata["Column mismatch"] = {
            "missing": list(set(expected_columns.keys()) - set(df.columns)),
            "unexpected": list(set(df.columns) - set(expected_columns.keys())),
        }

    # Check column data types
    type_mismatches = {
        col: {"expected": dtype, "actual": str(df[col].dtype).lower()}
        for col, dtype in expected_columns.items()
        if col in df and str(df[col].dtype).lower() != dtype
    }
    if type_mismatches:
        passed = False
        metadata["Type mismatches"] = type_mismatches

    # Check length of data
    if len(df) == 0:
        passed = False
        metadata["Error"] = "DataFrame is empty."

    return AssetCheckResult(
        passed=passed,
        metadata=metadata,
    )


def generate_expected_columns(model_class: Type[DeclarativeMeta]) -> dict:
    """
    Generate a dictionary mapping column names to their expected Pandas data types
    based on the SQLAlchemy model.

    Args:
        model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.

    Returns:
        dict: A dictionary where keys are column names and values are Pandas data types as strings.
    """
    # SQLAlchemy to Pandas type mapping
    type_mapping = {
        Integer: "int64",
        String: "object",
        Float: "float64",
        BigInteger: "int64",
    }

    # Generate the expected columns dictionary
    expected_columns = {
        column.name: type_mapping.get(
            type(column.type), "object"
        )  # Default to 'object'
        for column in model_class.__table__.columns
    }

    return expected_columns


def change_dataframe_column_types(
    df: pd.DataFrame, model_class: Type[DeclarativeMeta], context: AssetExecutionContext
):
    """
    Change the DataFrame column types to match the SQLAlchemy model definitions.

    Args:
        df (pd.DataFrame): The input DataFrame to modify.
        model_class (Type[DeclarativeMeta]): The SQLAlchemy model class.
        context (AssetExecutionContext): The execution context for logging.

    Returns:
        pd.DataFrame: The modified DataFrame with updated column types.
    """
    # Generate expected column types
    expected_types = generate_expected_columns(model_class)

    context.log.info("Changing DataFrame column types based on the ORM model.")
    context.log.info(f"Expected types: {expected_types}")

    for column, expected_type in expected_types.items():
        if column in df.columns:
            try:
                # Cast column to the expected type
                if expected_type in ["int64", "bigint"]:
                    df[column] = pd.to_numeric(
                        df[column], downcast="integer", errors="coerce"
                    ).astype("Int64")
                elif expected_type == "float64":
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                elif expected_type == "object":
                    df[column] = df[column].astype("object")
                context.log.info(
                    f"Column '{column}' converted to type '{expected_type}'."
                )
            except Exception as e:
                context.log.warning(
                    f"Failed to convert column '{column}' to type '{expected_type}': {e}. Keeping original type."
                )

    return df

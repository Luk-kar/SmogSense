"""Utility functions for logging information about DataFrames."""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
)


def log_dataframe_info(
    context: AssetExecutionContext, df: pd.DataFrame, df_name: str
) -> None:
    """Logs information about a DataFrame."""
    context.log.info(f"{df_name} shape:\n{df.shape}")
    context.log.info(f"{df_name} columns:\n{df.columns.tolist()}")
    context.log.info(f"{df_name} types:\n{df.dtypes}")
    context.log.info(f"{df_name} sample:\n{df.head(3)}")


def log_dataframe(
    context: AssetExecutionContext,
    message: str,
    df: pd.DataFrame,
) -> None:
    """
    Logs a message and a DataFrame in a standardized format.
    """

    context.log.info(message)
    context.log.info(f"\n{df.to_markdown(index=False)}")


def log_unique_values(context: AssetExecutionContext, df: pd.Series, label: str):
    """
    Logs the unique values of a given column in the dataframe.
    """

    unique_vals = df.unique()
    context.log.info(f"➡️ Unique {label}:\n{unique_vals}")


def log_columns_statistics(context: AssetExecutionContext, df: pd.DataFrame):
    """
    Logs descriptive statistics for each column in the DataFrame.
    """
    for column in df.columns:
        description = df.describe(include="all")[column]
        context.log.info(f"➡️ Description of '{column}':\n{description}")

        if column in ["name", "formula", "code"]:
            context.log.info(f"➡️ Unique values in '{column}':\n{df[column].unique()}")


def log_asset_materialization(
    context: AssetExecutionContext,
    asset_key: str,
    data_frame: pd.DataFrame,
    description: str,
) -> None:
    """Logs an AssetMaterialization event with metadata."""
    context.log_event(
        AssetMaterialization(
            asset_key=asset_key,
            description=description,
            metadata={
                "Number of records": MetadataValue.int(len(data_frame)),
                "Columns": MetadataValue.json(data_frame.columns.tolist()),
                "Data types": MetadataValue.json(
                    data_frame.dtypes.astype(str).to_dict()
                ),
                "Sample data": MetadataValue.md(data_frame.head(50).to_markdown()),
            },
        )
    )

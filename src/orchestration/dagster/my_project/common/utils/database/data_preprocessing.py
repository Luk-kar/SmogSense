"""
This module provides utility functions for data preprocessing 
in the context of an ETL pipeline using Dagster.
"""

# Python
from typing import Dict

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    Failure,
)


def map_foreign_keys_general(
    df: pd.DataFrame,
    mappings: Dict[str, Dict],
    context: AssetExecutionContext,
):
    """Map foreign keys in the DataFrame using provided mappings."""

    for column, mapping in mappings.items():

        df[f"id_{column}"] = df[column].map(mapping)

        # Check for missing mappings
        missing_values = df[df[f"id_{column}"].isnull()][column].unique()
        if len(missing_values) > 0:
            raise Failure(f"'{column}' not found in database: {missing_values}")

        # Optionally drop the original column
        df.drop(columns=[column], inplace=True)
        context.log.info(f"Mapped {column} to id_{column}")

    return df

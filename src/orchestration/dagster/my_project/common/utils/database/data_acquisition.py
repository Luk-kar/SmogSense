"""
Utility functions for data acquisition from databases.
"""

# Python
from typing import Union

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    Failure,
    MetadataValue,
)


def download_data(
    context: AssetExecutionContext,
    fetch_function: callable,
    asset_key: str,
) -> Union[list, dict]:
    """Generic function to download data with a check for empty records."""

    data: Union[list, dict] = fetch_function()
    num_records = len(data)

    if num_records == 0:
        raise Failure(f"No records fetched from the API for asset: {asset_key}")

    # Log the AssetMaterialization with metadata
    context.log_event(
        AssetMaterialization(
            asset_key=asset_key,
            metadata={"Number of records": MetadataValue.int(num_records)},
        )
    )

    return data

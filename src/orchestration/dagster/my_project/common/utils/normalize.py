"""
Utility functions to normalize data.
"""

# Python
from typing import Any

# Dagster
from dagster import AssetExecutionContext, Failure


def flatten_list(nested_list: list) -> list:
    """Make list without nested lists."""
    flattened = []

    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)

    return flattened


def flatten_data(context: AssetExecutionContext, data: Any) -> list:
    """
    Flatten the data to a list.
    """
    try:
        flattened_data = flatten_list(data)
        context.log.info("✅ Data flattened successfully.")

    except Exception as e:
        context.log.error(f"❌ Error flattening data:\n{e}")
        raise Failure(f"Failed to flatten data:\n{e}") from e
    return flattened_data

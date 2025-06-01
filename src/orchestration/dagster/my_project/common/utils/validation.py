"""
Validation functions for assets.
"""

# Python
from typing import Any

# Third-party
import pandas as pd
from typing import Any, Tuple

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetCheckResult,
    Failure,
)

# Pipeline
from common.utils.ORM import find_invalid_rows


def log_data_type_and_validate_if_list_or_dict(
    context: AssetExecutionContext, data: Any
) -> Any:
    """
    Log the data type and validate that the data is either a list or a dictionary,
    raising a Failure exception for invalid types.
    """
    if isinstance(data, list):
        context.log.info(f"➡️ Data is a list with {len(data)} records.")

    elif isinstance(data, dict):
        context.log.info(f"➡️ Data is a dictionary with {len(data)} records.")

    else:
        context.log.error("❌ Data is not a list or dictionary.")
        raise Failure("Data is not a list or dictionary.")


def check_dataframe_structure(
    df: pd.DataFrame, valid_columns: list[str]
) -> AssetCheckResult:
    """
    Checks if the dataframe has the expected columns.
    """

    df_columns = df.columns.tolist()
    difference = set(df_columns) - set(valid_columns)

    if difference:

        return AssetCheckResult(
            passed=False,
            metadata={
                "Invalid columns": df_columns,
                "Expected columns": valid_columns,
                "Difference": list(difference),
            },
        )

    return AssetCheckResult(passed=True, metadata={"Valid columns": df_columns})


def check_non_empty_dataframe(df: pd.DataFrame) -> AssetCheckResult:
    """
    Checks if the dataframe is empty.
    """

    if df.empty:
        return AssetCheckResult(passed=False, metadata={"error": "Data is empty"})

    return AssetCheckResult(passed=True)


def check_non_empty_values(df: pd.DataFrame, model) -> AssetCheckResult:
    """
    Checks if the dataframe has empty values.
    """

    invalid_rows = find_invalid_rows(df, model)

    passed = invalid_rows.empty

    metadata = {
        "Total rows": len(df),
        "Invalid rows": invalid_rows.to_dict(orient="records") if not passed else [],
    }

    return AssetCheckResult(passed=passed, metadata=metadata)


def validate_keys(
    record: dict, expected_keys: set, record_id: Any = None
) -> Tuple[bool, dict]:
    """
    Validates if the record has the expected keys.
    """

    record_keys = set(record.keys())
    missing_keys = expected_keys - record_keys
    surplus_keys = record_keys - expected_keys

    result_metadata = {}
    passed = True

    if missing_keys:
        result_metadata["missing_keys"] = list(missing_keys)
        passed = False
    if surplus_keys:
        result_metadata["surplus_keys"] = list(surplus_keys)
        passed = False

    if record_id is not None:
        result_metadata["record_id"] = record_id

    return passed, result_metadata

"""
Contains the assets for data processing of the 'air quality sensor' data.
"""

# Python
from typing import Any

# Third-party
import pandas as pd

# Dagster
from dagster import (
    asset,
    AssetExecutionContext,
    Failure,
)

# Pipeline
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    SensorGroups,
)
from common.utils.logging import (
    log_asset_materialization,
    log_columns_statistics,
)
from common.utils.normalize import (
    flatten_data,
)
from common.utils.dataframe import (
    convert_to_dataframe,
)
from common.utils.validation import (
    log_data_type_and_validate_if_list_or_dict,
)


@asset(
    group_name=SensorGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.SENSOR_DATA,
        )
    },
)
def flatten_and_sanitize_air_quality_sensor_data(
    context: AssetExecutionContext,
    download_air_quality_sensor_data_from_minio: Any,  # Union[list, dict]
) -> pd.DataFrame:
    """Transforms downloaded 'air quality sensor' data."""

    data = download_air_quality_sensor_data_from_minio

    log_data_type_and_validate_if_list_or_dict(context, data)

    flattened_data = flatten_data(context, data)

    df = convert_to_dataframe(context, flattened_data)

    df = process_parameter_column(context, df)

    df = ensure_correct_data_types(context, df)

    describe_df(context, df)

    ensure_there_is_no_nulls(df)

    log_asset_materialization(
        context=context,
        asset_key="flatten_and_sanitize_air_quality_sensor_data",
        description="Flattened and sanitized 'air quality sensor' data.",
        data_frame=df,
    )

    return df


def process_parameter_column(
    context: AssetExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Splits the 'param' column into multiple columns with database-like naming conventions.
    """
    # Ensure 'param' column exists and is not empty
    if "param" not in df.columns:
        raise ValueError("❌ The DataFrame does not contain a 'param' column.")

    context.log.info("➡️ Splitting the 'param' column into separate columns.")
    param_df = pd.json_normalize(df["param"])  # Flatten the 'param' dictionaries

    # Rename columns to match database-like naming conventions
    param_df.rename(
        columns={
            "paramName": "name",  # Matches the `name` column in the database
            "paramFormula": "formula",  # A formula-like representation
            "paramCode": "code",  # Code to represent the parameter
            "idParam": "id_indicator",  # Match primary key naming style
        },
        inplace=True,
    )

    # Drop the original 'param' column and concatenate new columns to the DataFrame
    df = df.drop(columns=["param"])
    df = pd.concat([df, param_df], axis=1)

    # Log the transformation
    context.log.info(f"✅ Processed DataFrame columns: {list(df.columns)}")

    return df


def ensure_correct_data_types(
    context: AssetExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Ensures the DataFrame has the correct data types.
    """

    CORRECT_DATA_TYPES = {
        "code": "object",
        "formula": "object",
        "id": "int64",
        "id_indicator": "int64",
        "name": "object",
        "stationId": "int64",
    }

    for column, dtype in CORRECT_DATA_TYPES.items():
        if column not in df.columns:
            raise ValueError(f"❌ DataFrame is missing the '{column}' column.")

        if df[column].dtype != dtype:
            context.log.info(f"➡️ Converting '{column}' to {dtype}.")
            df[column] = df[column].astype(dtype)

    return df


def describe_df(context: AssetExecutionContext, df: pd.DataFrame):
    """
    Describes the DataFrame with basic statistics, unique values, and null checks.
    """

    context.log.info("➡️ Describing the DataFrame.")

    log_columns_statistics(context, df)
    compare_unique_code_and_formula(context, df)
    check_for_null_and_empty_values(context, df)


def compare_unique_code_and_formula(context: AssetExecutionContext, df: pd.DataFrame):
    """
    Compares the unique values in 'code' and 'formula' columns.
    """
    context.log.info("➡️ Checking if unique code is the same as unique formula.")
    unique_code = df["code"].unique()
    unique_formula = df["formula"].unique()

    if len(unique_code) == len(unique_formula):
        context.log.info("✅ Unique code is the same as unique formula")
    else:
        context.log.warning("❌ Unique code is not the same as unique formula")
        context.log.warning(
            f"Unique code:\n{unique_code}\nUnique formula:\n{unique_formula}"
            f"\nThe difference:{set(unique_code) - set(unique_formula)}"
        )


def check_for_null_and_empty_values(context: AssetExecutionContext, df: pd.DataFrame):
    """
    Checks for null values and empty strings in the DataFrame.
    """
    context.log.info("➡️ Checking for null values and empty strings in the DataFrame.")

    # Replace empty strings with None for null checks
    df_processed_for_nulls = replace_empty_strings_with_none(df)

    null_counts = df_processed_for_nulls.isnull().sum()
    null_columns = null_counts[null_counts > 0]

    if not null_columns.empty:
        context.log.warning("❌ Columns with null values.")
        context.log.warning(null_columns)

        rows_with_nulls = df_processed_for_nulls[
            df_processed_for_nulls.isnull().any(axis=1)
        ]
        num_rows_with_nulls = len(rows_with_nulls)

        if num_rows_with_nulls > 0:
            context.log.warning(
                f"❌ Number of rows with null values:\n{num_rows_with_nulls}"
            )
            context.log.warning(
                f"❌ Sample rows with null values:\n{rows_with_nulls.head(3)}"
            )
    else:
        context.log.info("✅ No null values found in the data.")


def replace_empty_strings_with_none(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces empty strings with None in the DataFrame.
    """

    return df.replace(
        to_replace=r"^\s*$",
        value=None,
        regex=True,
    )


def ensure_there_is_no_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures there are no null values in the DataFrame.
    """

    df = replace_empty_strings_with_none(df)

    if df.isnull().values.any():
        raise Failure("❌ DataFrame contains null values.")
    return df


@asset(
    group_name=SensorGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
        )
    },
)
def rename_values_and_columns_air_quality_sensor_data(
    context: AssetExecutionContext,
    flatten_and_sanitize_air_quality_sensor_data: Any,
) -> pd.DataFrame:
    """Renames columns and translates values in the 'air quality sensor' data."""

    data = flatten_and_sanitize_air_quality_sensor_data

    context.log.info("➡️ Translating values")

    translations = {
        "dwutlenek azotu": "nitrogen dioxide",
        "ozon": "ozone",
        "dwutlenek siarki": "sulfur dioxide",
        "benzen": "benzene",
        "tlenek węgla": "carbon monoxide",
        "pył zawieszony PM2.5": "particulate matter PM2.5",
        "pył zawieszony PM10": "particulate matter PM10",
    }

    # check if there are any missing translations
    missing_translations = set(data["name"].unique()) - set(translations.keys())

    if missing_translations:
        raise ValueError(("❌ Missing translations:\n" f"{missing_translations}"))

    # translate name column
    data["name"] = data["name"].map(translations)

    context.log.info("✅ Values translated successfully.")

    data = rename_sensor_id_column(context, data)

    log_asset_materialization(
        context=context,
        data_frame=data,
        asset_key="rename_values_and_columns_air_quality_sensor_data",
        description="Air quality annual statistics data with columns and values translated",
    )

    return data


def rename_sensor_id_column(
    context: AssetExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Renames the 'id' column to 'id_sensor'.
    """

    translation = {
        "id": "id_sensor",
        "stationId": "id_station",
    }

    context.log.info(f"➡️ Renaming the:\n{translation}")

    if "id" not in df.columns:
        raise ValueError("❌ The DataFrame does not contain an 'id' column.")

    df_renamed = df.rename(
        columns={
            "id": "id_sensor",
            "stationId": "id_station",
        }
    )

    context.log.info(
        (
            "✅ Column renamed successfully!\n"
            "Current columns:\n"
            f"{df_renamed.columns}"
        )
    )

    return df_renamed

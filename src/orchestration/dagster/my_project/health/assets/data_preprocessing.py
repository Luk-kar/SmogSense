"""
Contains the assets for data processing of the 'air quality station' data.
"""

# Python
from typing import Any

# Third-party
import pandas as pd

# Dagster
from dagster import (
    asset,
    AssetExecutionContext,
    AssetMaterialization,
    Failure,
    MetadataValue,
)

# Common
from common.constants import get_metadata_categories
from common.utils.dataframe import (
    convert_to_dataframe,
)

# Pipeline
from health.constants import (
    HealthGroups,
    HealthAssetCategories as Categories,
)


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_PROCESSING,
            Categories.DATA_MODELING,
            Categories.HEALTH_DATA,
            Categories.MEASUREMENT,
            Categories.PROVINCE,
            Categories.DEATH_ILLNESS,
        )
    },
)
def extract_and_format_health_data(
    context: AssetExecutionContext, download_health_death_illness_data_from_minio: dict
) -> dict[str, pd.DataFrame]:
    """
    Extracts and formats the health data from the given JSON data
    into 3 separate DataFrames: illness, province, and measurement data.
    """

    data = download_health_death_illness_data_from_minio

    illness_data, province_data, measurement_data = extract_health_data(data)

    tables_candidates = {
        "illness_df": illness_data,
        "province_df": province_data,
        "measurement_df": measurement_data,
    }

    tables_candidates = format_and_log_dataframes(context, tables_candidates)

    context.log.info("✅ Data extracted successfully.")
    context.log.info(
        "Final dict:\n"
        f"len: {len(tables_candidates)}\n"
        f"keys: {tables_candidates}\n"
        f"values:\n{tables_candidates}"
    )

    return tables_candidates


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_PROCESSING,
            Categories.DEATH_ILLNESS,
            Categories.PROVINCE,
        )
    },
)
def lower_characters_in_province_column(
    context: AssetExecutionContext,
    extract_and_format_health_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Lower characters in the 'province' column of the 'province_df' DataFrame.
    """

    df = extract_and_format_health_data["province_df"]

    context.log.info(f"Data shape: {df.shape}")

    try:
        df["province"] = df["province"].str.lower()

        context.log.info("✅ Lower characters in 'province' column successfully.")
        context.log.info(f"➡️ Data sample after lowering:\n{df.head(3)}")

    except Exception as e:
        context.log.error(f"❌ Error lowering characters in 'province' column: {e}")
        raise Failure(f"Failed to lower characters in 'province' column: {e}") from e

    return df


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_PROCESSING,
            Categories.DEATH_ILLNESS,
        )
    },
)
def rename_columns_death_illness_data(
    context: AssetExecutionContext,
    extract_and_format_health_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Rename columns to standard names for the 'illness_df' DataFrame.
    """

    df = extract_and_format_health_data["illness_df"]

    context.log.info(f"Data shape: {df.shape}")

    try:
        columns_renamed = {
            "variableId": "id_illness",
            "name": "illness",
        }
        df = df.rename(columns=columns_renamed)

        context.log.info(f"✅ Columns renamed successfully:\n{df.columns}")
        context.log.info(f"➡️ Data sample after renaming:\n{df.head(3)}")

        context.log_event(
            AssetMaterialization(
                asset_key="rename_columns_death_illness_data",
                description="Columns renamed successfully.",
                metadata={
                    "Columns before renaming": MetadataValue.json(df.columns.tolist()),
                    "Columns renamed": MetadataValue.json(df.columns.tolist()),
                },
            )
        )

    except Exception as e:
        context.log.error(f"❌ Error renaming columns: {e}")
        raise Failure(f"Failed to rename columns: {e}") from e

    return df


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_PROCESSING,
            Categories.MEASUREMENT,
        )
    },
)
def rename_columns_measurement_data(
    context: AssetExecutionContext,
    extract_and_format_health_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Rename columns to standard names for the 'measurement_df' DataFrame.
    """

    df = extract_and_format_health_data["measurement_df"]

    context.log.info(f"Data shape: {df.shape}")

    try:
        columns_renamed = {
            "variableId": "id_illness",
            "val": "deaths",
        }
        df = df.rename(columns=columns_renamed)

        context.log.info(f"✅ Columns renamed successfully:\n{df.columns}")
        context.log.info(f"➡️ Data sample after renaming:\n{df.head(3)}")

        context.log_event(
            AssetMaterialization(
                asset_key="rename_columns_measurement_data",
                description="Columns renamed successfully.",
                metadata={
                    "Columns before renaming": MetadataValue.json(df.columns.tolist()),
                    "Columns renamed": MetadataValue.json(df.columns.tolist()),
                },
            )
        )

    except Exception as e:
        context.log.error(f"❌ Error renaming columns: {e}")
        raise Failure(f"Failed to rename columns: {e}") from e

    return df


def format_and_log_dataframes(
    context: AssetExecutionContext, tables_candidates: dict[str, Any]
) -> dict[str, pd.DataFrame]:
    """
    Converts the given tables candidates to DataFrames and logs summary statistics.
    """

    for table_name, table_data in tables_candidates.items():
        if table_data is None:
            context.log.error(f"❌ No data found for '{table_name}' table.")
            raise Failure(f"No data found for '{table_name}' table.")

        df = convert_to_dataframe(context, table_data)
        tables_candidates[table_name] = df

        context.log.info(
            f"🔍 Summary statistics for '{table_name}':\n{df.describe().to_string()}"
        )

        # Analyze unique values for string columns
        log_unique_values_summary(context, table_name, df)

    return tables_candidates


def log_unique_values_summary(
    context: AssetExecutionContext, table_name: str, df: pd.DataFrame
):
    """
    Logs the unique values summary for the given DataFrame.
    """

    string_columns = df.select_dtypes(include=["object"]).columns

    for col in string_columns:
        unique_values = df[col].unique()
        unique_count = len(unique_values)
        all_unique = len(df) == unique_count
        diff_len_unique = len(df) - unique_count

        context.log.info(
            f"🔎 Column '{col}' in '{table_name}' has {unique_count} unique values."
        )
        context.log.info(
            (
                "   - Are all values unique?\n"
                f"     {'✅ Yes' if all_unique else '❌ No'}"
            )
        )
        if not all_unique:
            context.log.info(f"   - Difference in length: {diff_len_unique}")

        context.log.info(f"   - First 50 unique values: {list(unique_values[:50])}")


def extract_health_data(json_data: dict):
    """
    Extracts illness data, province data, and measurement data from the given JSON data.

    Args:
        json_data (dict): The JSON data containing health-related records.

    Returns:
        tuple: (illness_data, province_data, measurement_data) as lists of dictionaries.
    """

    illness_data = []
    province_data = []
    measurement_data = []

    for _id, variable_info in json_data.items():

        variable_id = variable_info.get("variableId")

        # Illness metadata
        illness_data.append(
            {
                "variableId": variable_id,
                "name": variable_info.get("name"),
            }
        )

        # Process results
        results = variable_info.get("results", [])

        for result in results:

            province_id = result.get("id")

            # Province metadata
            province_data.append(
                {
                    "id_province": province_id,
                    "province": result.get("name"),
                }
            )

            # Yearly measurements
            for value in result.get("values", []):
                measurement_data.append(
                    {
                        "variableId": variable_id,
                        "id_province": province_id,
                        "year": value.get("year"),
                        "val": value.get("val"),
                    }
                )

    # Ensure unique province data
    province_data = {
        frozenset(entry.items()): entry for entry in province_data
    }.values()

    return list(illness_data), list(province_data), list(measurement_data)


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_PROCESSING,
            Categories.DATA_MODELING,
            Categories.HEALTH_DATA,
            Categories.MEASUREMENT,
            Categories.PROVINCE,
            Categories.DEATH_ILLNESS,
        )
    },
)
def extract_and_format_country_people_total_data(
    context: AssetExecutionContext,
    download_country_total_people_yearly_data_from_minio: dict,
) -> pd.DataFrame:
    """
    Extracts and formats the country people total data from the given JSON data.
    """

    data = list(download_country_total_people_yearly_data_from_minio.values())[0]

    records = data["results"][0]["values"]

    df = convert_to_dataframe(context, records)

    df.drop(columns=["attrId"], inplace=True)

    df.rename(columns={"val": "people_total"}, inplace=True)

    df["year"] = df["year"].astype(int)

    context.log.info("✅ Data extracted successfully.")
    context.log.info(f"Data shape: {df.shape}")
    context.log.info(f"➡️ Data sample:\n{df.head(3)}")
    context.log.info(f"🔍 Summary statistics:\n{df.describe().to_string()}")

    return df


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_PROCESSING,
            Categories.DATA_MODELING,
            Categories.HEALTH_DATA,
            Categories.MEASUREMENT,
            Categories.PROVINCE,
            Categories.DEATH_ILLNESS,
        )
    },
)
def extract_and_format_province_people_total_data(
    context: AssetExecutionContext,
    download_province_total_people_yearly_data_from_minio: dict,
) -> pd.DataFrame:
    """
    Extracts and formats the province people total data from the given JSON data.
    """

    data = list(download_province_total_people_yearly_data_from_minio.values())[0]

    records = data["results"]

    df = convert_to_dataframe(context, records)

    flattened_data = []
    for _, row in df.iterrows():
        name = row["name"]
        values = row["values"]
        for entry in values:
            flattened_data.append(
                {
                    "province": name,
                    "year": int(entry["year"]),
                    "people_total": entry["val"],
                }
            )

    # Create a new DataFrame from the flattened data
    flattened_df = pd.DataFrame(flattened_data)

    context.log.info("✅ Data extracted and flattened successfully.")
    context.log.info(f"Flattened data shape: {flattened_df.shape}")
    context.log.info(f"➡️ Flattened data sample:\n{flattened_df.head(3)}")
    context.log.info(f"🔍 Summary statistics:\n{flattened_df.describe().to_string()}")

    return flattened_df

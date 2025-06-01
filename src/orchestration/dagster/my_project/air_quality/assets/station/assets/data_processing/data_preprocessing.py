"""
Contains the assets for data processing of the 'air quality station' data.
"""

# Python
from typing import Any

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    Failure,
    MetadataValue,
    asset,
    TableRecord,
)

# Pipeline
from air_quality.assets.station.utils import (
    normalize_city_column,
)
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    StationGroups,
)
from common.utils.validation import (
    log_data_type_and_validate_if_list_or_dict,
)
from common.utils.logging import log_asset_materialization
from common.utils.normalize import (
    flatten_data,
)
from common.utils.dataframe import (
    convert_to_dataframe,
)


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.STATION_DATA,
        )
    },
)
def flatten_and_sanitize_air_quality_station_data(
    context: AssetExecutionContext,
    download_air_quality_station_data_from_minio: Any,  # Union[list, dict]
) -> pd.DataFrame:
    """Transforms downloaded 'air quality station' data."""

    data = download_air_quality_station_data_from_minio

    log_data_type_and_validate_if_list_or_dict(context, data)

    flattened_data = flatten_data(context, data)

    df = convert_to_dataframe(context, flattened_data)

    df = process_city_column(context, df)

    df = convert_data_types(context, df)

    log_asset_materialization(
        context=context,
        asset_key="flatten_and_sanitize_air_quality_station_data",
        description="Flattened and sanitized 'air quality station' data.",
        data_frame=df,
    )

    return df


def process_city_column(
    context: AssetExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Normalize the 'city' column in the 'air quality station' data.
    """
    try:
        # Assuming 'city' column needs normalization
        city_data = normalize_city_column(df["city"])

        # Drop the original 'city' column and merge with the normalized data
        df = df.drop(columns=["city"]).reset_index(drop=True)
        df = pd.concat([df, city_data], axis=1)

        context.log.info("✅ City column normalized successfully.")

        context.log.info(f"Transformed columns:\n{df.columns}")
        context.log.info(f"Transformed data sample:\n{df.head(1)}")
        context.log.info(f"Transformed data types:\n{df.dtypes}")

    except Exception as e:
        context.log.error(f"❌ Error during data transformation:\n{e}")
        raise Failure(f"Data transformation failed:\n{e}") from e
    return df


def convert_data_types(
    context: AssetExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """Convert data types of the 'air quality station' data."""

    try:
        df = df.astype(
            {
                "stationName": "object",  # older version of pandas does not support 'string' type
                "addressStreet": "object",
                "id": "int",
                "gegrLat": "float",
                "gegrLon": "float",
                "city": "object",
                "county": "object",
                "province": "object",
            }
        )

        context.log.info("✅ Data types converted successfully.")
        context.log.info(f"➡️ Data types after conversion:\n{df.dtypes}")

    except Exception as e:
        context.log.error(f"❌ Error converting data types: {e}")
        raise Failure(f"Failed to convert data types: {e}") from e
    return df


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.STATION_DATA,
        )
    },
)
def nulls_to_none_air_quality_station_data(
    context: AssetExecutionContext,
    flatten_and_sanitize_air_quality_station_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert null values to None in the 'air quality data'.
    to have valid null values in the postgres database when inserting.
    """

    df = flatten_and_sanitize_air_quality_station_data

    context.log.info(f"Data shape: {df.shape}")

    try:

        df = df.where(pd.notnull(df), None)

        # Handle empty strings or strings with only whitespace
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].apply(
                lambda x: None if isinstance(x, str) and x.strip() == "" else x
            )

        null_counts = df.isnull().sum()

        if df.isnull().sum().sum() > 0:

            context.log.info(f"➡️ Converted nulls to None:\n{null_counts}")

            null_count_report = [
                TableRecord({"Column": col, "Null Count": int(null_count)})
                for col, null_count in null_counts.items()
            ]

        else:

            null_count_report = TableRecord({"Column": "None", "Null Count": 0})

            context.log.info("✅ No null values found in the data.")

    except Exception as e:
        context.log.error(f"❌ Error converting nulls to None: {e}")
        raise Failure(f"Failed to convert nulls to None: {e}") from e

    # Log AssetMaterialization
    context.log_event(
        AssetMaterialization(
            asset_key="nulls_to_none_air_quality_station_data",
            description="Null values converted to None.",
            metadata={
                "Number of records": MetadataValue.int(len(df)),
                "Null counts by column": MetadataValue.table(null_count_report),
            },
        )
    )

    return df


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.STATION_DATA,
        )
    },
)
def renaming_columns_air_quality_station_data(
    context: AssetExecutionContext,
    nulls_to_none_air_quality_station_data: pd.DataFrame,
) -> pd.DataFrame:
    """Rename columns to standard names for the 'air quality station' data."""

    df_source = nulls_to_none_air_quality_station_data

    context.log.info(f"Data shape: {df_source.columns}")

    try:
        columns_renamed = {
            "stationName": "station_name",
            "addressStreet": "street_address",
            "id": "id_station",
            "gegrLat": "latitude",
            "gegrLon": "longitude",
        }
        df_renamed = df_source.rename(columns=columns_renamed)

        context.log.info(f"✅ Columns renamed successfully:\n{df_renamed.columns}")
        context.log.info(f"➡️ Data sample after renaming:\n{df_renamed.head(1)}")

    except Exception as e:
        context.log.error(f"❌ Error renaming columns: {e}")
        raise Failure(f"Failed to rename columns: {e}") from e

    # Log AssetMaterialization
    context.log_event(
        AssetMaterialization(
            asset_key="renaming_columns_air_quality_station_data",
            description="Columns renamed successfully.",
            metadata={
                "Columns before renaming": MetadataValue.json(
                    df_source.columns.tolist()
                ),
                "Columns renamed": MetadataValue.json(df_renamed.columns.tolist()),
            },
        )
    )

    return df_renamed

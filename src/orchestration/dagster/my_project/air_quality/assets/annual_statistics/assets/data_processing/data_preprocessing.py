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
    asset,
)

# Pipeline
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    AnnualStatisticsGroups,
)
from common.utils.logging import (
    log_asset_materialization,
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
# fmt: off
from air_quality.assets.\
    annual_statistics.\
    assets.data_processing.helpers.extract_records import (
        extract_records,
        check_candidates_for_integers,
        )
from air_quality.assets.\
    annual_statistics.\
    assets.data_processing.helpers.data_enriching import (
        add_time_columns_based_on_averaging,
        )
from air_quality.assets.\
    annual_statistics.\
    assets.data_processing.helpers.translate import (
        translate_time_averaging_column,
        translate_zone_name_and_extract_zone_type,
        translate_indicator_type_column,
        translate_column_names,
        )
# fmt: off

@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
        )
    },
)
def flatten_and_extract_air_quality_annual_statistics_data(
    context: AssetExecutionContext,
    download_air_quality_annual_statistics_data_from_minio: Any,
) -> pd.DataFrame:
    """Transforms downloaded 'air quality annual statistics' data into a DataFrame."""

    data = download_air_quality_annual_statistics_data_from_minio

    log_data_type_and_validate_if_list_or_dict(context, data)

    flattened_data = flatten_data(context, data)

    df = convert_to_dataframe(context, flattened_data)

    df_records = extract_records(context, df)

    check_candidates_for_integers(context, df_records)

    # check columns without NaN/None values
    context.log.info("➡️ Checking for columns without NaN/None values")

    non_null_columns = df_records.columns[df_records.notnull().all()].tolist()

    context.log.info(f"Columns without NaN/None values:\n{non_null_columns}")

    log_asset_materialization(
        context=context,
        data_frame=df_records,
        asset_key="flatten_and_extract_air_quality_annual_statistics_data",
        description="Air quality annual statistics data flattened and extracted",
    )

    return df_records

@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
        )
    },
)
def sanitize_air_quality_annual_statistics_data(
    context: AssetExecutionContext,
    flatten_and_extract_air_quality_annual_statistics_data: Any,
) -> pd.DataFrame:
    """Sanitizes the 'air quality annual statistics' data."""

    data = flatten_and_extract_air_quality_annual_statistics_data

    context.log.info("➡️ Sanitizing the 'air quality annual statistics' data")

    data = add_time_columns_based_on_averaging(context, data)

    log_asset_materialization(
        context=context,
        data_frame=data,
        asset_key="sanitize_air_quality_annual_statistics_data",
        description="Air quality annual statistics data sanitized",
    )

    return data


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
        )
    },
)
def nulls_to_none_air_quality_annual_statistics_data(
    context: AssetExecutionContext,
    sanitize_air_quality_annual_statistics_data: Any,
) -> pd.DataFrame:
    """Replaces NaN values with None in the 'air quality annual statistics' data."""

    data = sanitize_air_quality_annual_statistics_data

    context.log.info("➡️ Replacing NaN values with None")

    data = data.where(pd.notnull(data), None)

    log_asset_materialization(
        context=context,
        data_frame=data,
        asset_key="nulls_to_none_air_quality_annual_statistics_data",
        description="Air quality annual statistics data with NaN values replaced with None",
    )

    return data


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
        )
    },
)
def rename_columns_and_values_air_quality_annual_statistics_data(
    context: AssetExecutionContext,
    nulls_to_none_air_quality_annual_statistics_data: Any,
) -> pd.DataFrame:
    """Renames columns and translates values in the 'air quality annual statistics' data."""

    data = nulls_to_none_air_quality_annual_statistics_data

    context.log.info("➡️ Translating columns and values")

    data = translate_time_averaging_column(context, data)

    data = translate_zone_name_and_extract_zone_type(context, data)

    data = translate_indicator_type_column(context, data)

    data = translate_column_names(context, data)

    context.log.info(f"Columns after translation:\n{data.columns}")

    log_asset_materialization(
        context=context,
        data_frame=data,
        asset_key="rename_columns_and_values_air_quality_annual_statistics_data",
        description="Air quality annual statistics data with columns and values translated",
    )

    return data

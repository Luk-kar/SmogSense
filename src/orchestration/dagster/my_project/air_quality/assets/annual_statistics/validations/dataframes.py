"""
Module for validating the structure and contents of DataFrames 
related to air quality annual statistics using Dagster asset checks.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetKey,
    asset_check,
    AssetCheckResult,
)

# Pipeline
from air_quality.models.annual_statistics_models import (
    Province,
    ZoneType,
    Indicator,
    TimeAveraging,
    Measurement,
)
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.validation import (
    check_dataframe_structure,
    check_non_empty_dataframe,
)


@asset_check(
    asset=AssetKey("flatten_and_extract_air_quality_annual_statistics_data"),
)
def check_air_quality_annual_statistics_dataframe(
    flatten_and_extract_air_quality_annual_statistics_data: pd.DataFrame,
) -> AssetCheckResult:
    """Checks if data is 0 length"""

    return check_non_empty_dataframe(
        flatten_and_extract_air_quality_annual_statistics_data
    )


@asset_check(
    asset=AssetKey("create_dataframe_province_annual_statistics"),
)
def check_province_dataframe(
    create_dataframe_province: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'province' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Province)

    return check_dataframe_structure(
        create_dataframe_province,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_zone_type"),
)
def check_zone_type_dataframe(
    create_dataframe_zone_type: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'zone_type' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(ZoneType)

    return check_dataframe_structure(
        create_dataframe_zone_type,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_zone"),
)
def check_zone_dataframe(
    create_dataframe_zone: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'zone' DataFrame."""

    valid_columns = ["zone_code", "zone_name", "zone_type", "province"]

    return check_dataframe_structure(
        create_dataframe_zone,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_station_annual_statistics"),
)
def check_station_dataframe(
    create_dataframe_station: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'station' DataFrame."""

    valid_columns = ["station_code", "zone_code"]

    return check_dataframe_structure(
        create_dataframe_station,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_indicator"),
)
def check_indicator_dataframe(
    create_dataframe_indicator: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'indicator' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Indicator)

    return check_dataframe_structure(
        create_dataframe_indicator,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_time_averaging"),
)
def check_time_averaging_dataframe(
    create_dataframe_time_averaging: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'time_averaging' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(TimeAveraging)

    return check_dataframe_structure(
        create_dataframe_time_averaging,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_measurement"),
)
def check_measurement_dataframe(
    create_dataframe_measurement: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'measurement' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Measurement)

    valid_columns.extend(
        [
            "station_code",
            "time_averaging",
            "indicator_type",
            "zone_code",
        ]
    )

    return check_dataframe_structure(
        create_dataframe_measurement,
        valid_columns,
    )

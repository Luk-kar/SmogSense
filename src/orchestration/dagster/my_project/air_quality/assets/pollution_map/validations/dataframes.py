"""
Module for validating the structure and contents of DataFrames 
related to air quality pollution map data using Dagster asset checks.
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
from air_quality.models.map_pollution_models import (
    Pollutant,
)
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.validation import (
    check_dataframe_structure,
)


@asset_check(
    asset=AssetKey("download_air_quality_map_pollutant_data_from_minio"),
)
def check_download_air_quality_map_pollutant_data_from_minio(
    download_air_quality_map_pollutant_data_from_minio: dict,
) -> AssetCheckResult:
    """Checks if data is 0 length"""

    if not download_air_quality_map_pollutant_data_from_minio:
        return AssetCheckResult(
            passed=False,
            description="No data was downloaded from Minio.",
        )

    return AssetCheckResult(passed=True)


@asset_check(
    asset=AssetKey("create_dataframe_map_pollutants"),
)
def check_pollutant_dataframe(
    create_dataframe_map_pollutants: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'pollutant' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Pollutant)

    return check_dataframe_structure(
        create_dataframe_map_pollutants,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_map_measurements"),
)
def check_measurement_dataframe(
    create_dataframe_map_measurements: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'measurement' DataFrame."""

    valid_columns = ["pollutant_name", "data_year", "date_published"]

    return check_dataframe_structure(
        create_dataframe_map_measurements,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_map_geometry"),
)
def check_geometry_dataframe(
    create_dataframe_map_geometry: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'geometry' DataFrame."""

    valid_columns = ["year", "pollutant_name", "geometry", "value"]

    return check_dataframe_structure(
        create_dataframe_map_geometry,
        valid_columns,
    )

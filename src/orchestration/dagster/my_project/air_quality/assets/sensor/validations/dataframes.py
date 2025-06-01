"""
Defines Dagster asset checks for validating the structure and quality
of DataFrames representing 'air quality station' data.
It includes checks for schema conformity, non-empty fields,
and valid geographic coordinates.
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
from air_quality.models.sensor_models import (
    Indicator,
    Sensor,
)
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.validation import (
    check_dataframe_structure,
    check_non_empty_dataframe,
)


@asset_check(
    asset=AssetKey("flatten_and_sanitize_air_quality_sensor_data"),
)
def check_air_quality_sensor_dataframe(
    flatten_and_sanitize_air_quality_sensor_data: pd.DataFrame,
) -> AssetCheckResult:
    """Checks if data is 0 length"""

    return check_non_empty_dataframe(flatten_and_sanitize_air_quality_sensor_data)


@asset_check(
    asset=AssetKey("create_dataframe_sensor_indicator"),
)
def check_sensor_indicator_dataframe(
    create_dataframe_sensor_indicator: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'sensor_indicator' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Indicator)

    return check_dataframe_structure(
        create_dataframe_sensor_indicator,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_sensor"),
)
def check_sensor_dataframe(
    create_dataframe_sensor: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'sensor' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Sensor)

    return check_dataframe_structure(
        create_dataframe_sensor,
        valid_columns,
    )

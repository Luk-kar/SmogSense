"""
Data modeling assets for the 'air quality sensor' data.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    Failure,
    asset,
)

# Pipeline
from common.utils.dataframe import (
    apply_default_ordering,
    ensure_dataframe_columns_match_model,
)
from air_quality.models.sensor_models import (
    Indicator,
    Sensor,
)
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    SensorGroups,
)
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.dataframe import drop_rows_with_nulls
from common.utils.logging import (
    log_dataframe_info,
    log_asset_materialization,
)


@asset(
    group_name=SensorGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.SENSOR_DATA,
            Categories.INDICATOR_TABLE,
        ),
    },
)
def create_dataframe_sensor_indicator(
    context: AssetExecutionContext,
    rename_values_and_columns_air_quality_sensor_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Creates 'indicator' DataFrame from the sanitized 'air quality sensor' data.
    """
    try:
        df_source = rename_values_and_columns_air_quality_sensor_data

        log_dataframe_info(context, df_source, "Data source")

        # Extract relevant columns for Indicator
        df_indicator = df_source[
            ["id_indicator", "name", "formula", "code"]
        ].drop_duplicates()

        # Drop rows with nulls based on the Indicator model constraints
        df_indicator = drop_rows_with_nulls(df_indicator, Indicator)

        # Apply default ordering
        df_indicator = apply_default_ordering(df_indicator, Indicator, context)

        # Get model columns excluding primary keys and generated columns
        model_values_columns = get_model_non_primary_keys_and_non_generated_columns(
            Indicator
        )

        # Reorder DataFrame columns to match model columns
        df_indicator = df_indicator[model_values_columns]

        # Ensure DataFrame columns match the ORM model
        ensure_dataframe_columns_match_model(df_indicator, Indicator)

        context.log.info(
            f"'indicator' DataFrame created successfully.\n{df_indicator.head(3)}"
        )

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            asset_key="create_dataframe_sensor_indicator",
            description="Indicator DataFrame created",
            data_frame=df_indicator,
        )

        return df_indicator

    except Exception as e:
        context.log.error(f"Error creating 'indicator' DataFrame: {e}")
        raise Failure(f"Failed to create 'indicator' DataFrame: {e}") from e


@asset(
    group_name=SensorGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.SENSOR_DATA,
            Categories.SENSOR_TABLE,
        ),
    },
)
def create_dataframe_sensor(
    context: AssetExecutionContext,
    rename_values_and_columns_air_quality_sensor_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Creates 'sensor' DataFrame from the sanitized 'air quality sensor' data.
    """
    try:
        df_source = rename_values_and_columns_air_quality_sensor_data

        log_dataframe_info(context, df_source, "Data source")

        # Extract relevant columns for Sensor
        df_sensor = df_source[
            ["id_sensor", "id_station", "id_indicator"]
        ].drop_duplicates()

        # Drop rows with nulls based on the Sensor model constraints
        df_sensor = drop_rows_with_nulls(df_sensor, Sensor)

        # Apply default ordering
        df_sensor = apply_default_ordering(df_sensor, Sensor, context)

        # Get model columns excluding primary keys and generated columns
        model_values_columns = get_model_non_primary_keys_and_non_generated_columns(
            Sensor
        )

        # Reorder DataFrame columns to match model columns
        df_sensor = df_sensor[model_values_columns]

        # Ensure DataFrame columns match the ORM model
        ensure_dataframe_columns_match_model(df_sensor, Sensor)

        context.log.info(
            f"'sensor' DataFrame created successfully.\n{df_sensor.head(3)}"
        )

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            asset_key="create_dataframe_sensor",
            description="Sensor DataFrame created",
            data_frame=df_sensor,
        )

        return df_sensor

    except Exception as e:
        context.log.error(f"Error creating 'sensor' DataFrame: {e}")
        raise Failure(f"Failed to create 'sensor' DataFrame: {e}") from e

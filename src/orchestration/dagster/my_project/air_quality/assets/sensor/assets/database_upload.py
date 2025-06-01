"""
Contains the assets that are used to upload 'air quality sensor' data to the PostgreSQL database.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    asset,
    AssetExecutionContext,
)

# Pipeline
from air_quality.models.sensor_models import (
    Indicator,
    Sensor,
)
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    SensorGroups,
)
from common.utils.database.data_ingestion import (
    upload_data_and_log_materialization,
)


@asset(
    group_name=SensorGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.SENSOR_DATA,
            Categories.INDICATOR_TABLE,
        )
    },
)
def upload_data_sensor_indicator(
    context: AssetExecutionContext,
    create_dataframe_sensor_indicator: pd.DataFrame,
):
    """Upload 'indicator' data to PostgreSQL database"""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_sensor_indicator,
        model_class=Indicator,
        asset_key_str="upload_data_sensor_indicator",
        description="Uploaded 'indicator' data to PostgreSQL database.",
    )


@asset(
    group_name=SensorGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={"upload_data_sensor_indicator"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.SENSOR_DATA,
            Categories.INDICATOR_TABLE,
        )
    },
)
def upload_data_sensor(
    context: AssetExecutionContext,
    create_dataframe_sensor: pd.DataFrame,
):
    """Upload 'sensor' data to PostgreSQL database"""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_sensor,
        model_class=Sensor,
        asset_key_str="upload_data_sensor",
        description="Uploaded 'sensor' data to PostgreSQL database.",
    )

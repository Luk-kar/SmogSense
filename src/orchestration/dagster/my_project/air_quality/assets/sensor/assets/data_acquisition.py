"""
Contains assets for downloading 'air quality sensors' data from the API.
"""

# Air quality
from src.data_acquisition.air_quality import fetch_sensor_data_all

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)

# Pipeline
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    SensorGroups,
)
from common.utils.database.data_acquisition import (
    download_data,
)


@asset(
    group_name=SensorGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_ACQUISITION,
            Categories.SENSOR_DATA,
        )
    },
)
def download_air_quality_sensor_data(context: AssetExecutionContext) -> list:
    """Download 'air quality sensors' data from the API."""

    return download_data(
        context=context,
        fetch_function=fetch_sensor_data_all,
        asset_key="download_air_quality_sensor_data",
    )

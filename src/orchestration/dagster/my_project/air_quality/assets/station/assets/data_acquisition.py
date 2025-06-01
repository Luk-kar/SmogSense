"""
Contains assets for downloading 'air quality station' data from the API.
"""

# Air quality
from src.data_acquisition.air_quality import fetch_station_data

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)

# Pipeline
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    StationGroups,
)
from common.utils.database.data_acquisition import (
    download_data,
)


@asset(
    group_name=StationGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_ACQUISITION,
            Categories.STATION_DATA,
        )
    },
)
def download_air_quality_station_data(context: AssetExecutionContext) -> list:
    """Download 'air quality station' data and save to local storage (via IO Manager)."""

    return download_data(
        context=context,
        fetch_function=fetch_station_data,
        asset_key="download_air_quality_station_data",
    )

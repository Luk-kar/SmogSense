"""
Contains assets for downloading 'air quality station' data from the API.
"""

# Air quality
from src.data_acquisition.air_quality import fetch_annual_statistics_all

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
from common.utils.database.data_acquisition import (
    download_data,
)


@asset(
    group_name=AnnualStatisticsGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_ACQUISITION,
            Categories.ANNUAL_STATISTICS_DATA,
        )
    },
)
def download_air_quality_annual_statistics_data(context: AssetExecutionContext) -> list:
    """Download 'air quality annual statistics' data from the API."""

    return download_data(
        context=context,
        fetch_function=fetch_annual_statistics_all,
        asset_key="download_air_quality_annual_statistics_data",
    )

"""
Contains assets for downloading 'social media' data and saving it to local storage.
"""

# Air quality
from src.data_acquisition.territory.api_client import (
    fetch_provinces_data,
)

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)

# Pipeline
from common.constants import get_metadata_categories
from common.utils.database.data_acquisition import (
    download_data,
)
from territory.assets.constants import (
    TerritoryAssetCategories as Categories,
    Groups as TerritoryGroups,
)


@asset(
    group_name=TerritoryGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.TERRITORY,
            Categories.DATA_ACQUISITION,
        )
    },
)
def download_provinces_data(context: AssetExecutionContext) -> dict:
    """Download 'provinces' data from the Twitter API."""

    return download_data(
        context=context,
        fetch_function=fetch_provinces_data,
        asset_key="download_air_quality_provinces_data",
    )

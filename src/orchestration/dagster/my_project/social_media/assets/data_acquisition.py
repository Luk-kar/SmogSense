"""
Contains assets for downloading 'social media' data and saving it to local storage.
"""

# Air quality
from src.data_acquisition.social_media.main import run_acquisition

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
from social_media.assets.constants import (
    SocialMediaAssetCategories as Categories,
    Groups as SocialMediaGroups,
)


@asset(
    group_name=SocialMediaGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATA_ACQUISITION,
            Categories.TWEET_DATA,
        )
    },
)
def download_social_media_data(context: AssetExecutionContext) -> list:
    """Download 'social media' data from the Twitter API."""

    return download_data(
        context=context,
        fetch_function=run_acquisition,
        asset_key="download_air_quality_social_media_data",
    )

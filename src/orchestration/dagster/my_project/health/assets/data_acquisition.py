"""
Contains assets for downloading 'health death & illness' data from the API.
"""

# Dagster
from dagster import AssetExecutionContext, asset

# Pipeline
from health.constants import (
    HealthGroups,
    HealthAssetCategories as Categories,
)

# Common
from common.constants import get_metadata_categories
from common.utils.database.data_acquisition import download_data

# Health
from src.data_acquisition.health.pollution_health_data_fetcher import (
    fetch_air_pollution_related_death_data,
    fetch_province_total_people_yearly_data,
    fetch_country_total_people_yearly_data,
)


@asset(
    group_name=HealthGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_ACQUISITION,
            Categories.HEALTH_DATA,
        )
    },
)
def download_health_death_illness_data(context: AssetExecutionContext) -> dict:
    """
    Download 'health death & illness' data and save to local storage (via IO Manager).
    """

    return download_data(
        context=context,
        fetch_function=fetch_air_pollution_related_death_data,
        asset_key="download_health_death_illness_data",
    )


@asset(
    group_name=HealthGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_ACQUISITION,
            Categories.DEMOGRAPHIC,
        )
    },
)
def download_province_total_people_yearly_data(context: AssetExecutionContext) -> dict:
    """
    Download the total number of people in the province yearly.
    """

    return download_data(
        context=context,
        fetch_function=fetch_province_total_people_yearly_data,
        asset_key="download_province_total_people_yearly_data",
    )


@asset(
    group_name=HealthGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.DATA_ACQUISITION,
            Categories.DEMOGRAPHIC,
        )
    },
)
def download_country_total_people_yearly_data(context: AssetExecutionContext) -> dict:
    """
    Download the total number of people in the country yearly.
    """

    return download_data(
        context=context,
        fetch_function=fetch_country_total_people_yearly_data,
        asset_key="download_country_total_people_yearly_data",
    )

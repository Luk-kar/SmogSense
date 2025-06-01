"""
Contains assets for downloading 'air quality map pollutant concentration distribution' data.

Due to the size of the data and free API limitation,
the asset is divided into the 3 most important pollutants:
- PM2.5
- NO2
- O3
Choice is based on:
https://www.eea.europa.eu/publications/harm-to-human-health-from-air-pollution
"""

# Air quality
from src.data_acquisition.air_quality import (
    fetch_map_pollutant_concentration_distribution,
)
from src.data_acquisition.air_quality.api_endpoints import (
    MAP_POLLUTANT_ARGS,
)


# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
    StaticPartitionsDefinition,
)

# Pipeline
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    MapPollutantGroups,
)
from common.utils.database.data_acquisition import (
    download_data,
)

INDICATOR_TYPE = MAP_POLLUTANT_ARGS["indicatorType"]["Health care indicator"]

CHOSEN_POLLUTANTS = [
    MAP_POLLUTANT_ARGS["indicator"][INDICATOR_TYPE]["Particulate Matter 2.5 (annual)"],
    MAP_POLLUTANT_ARGS["indicator"][INDICATOR_TYPE]["Nitrogen Dioxide (annual)"],
    MAP_POLLUTANT_ARGS["indicator"][INDICATOR_TYPE]["Ozone (3-year)"],
]


MOST_RECENT_YEAR = sorted(MAP_POLLUTANT_ARGS["year"], reverse=True)[0]

# The individual pollutants are big so they are downloaded separately
partitions_def = StaticPartitionsDefinition(partition_keys=CHOSEN_POLLUTANTS)


@asset(
    group_name=MapPollutantGroups.DATA_ACQUISITION,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_ACQUISITION,
            Categories.SENSOR_DATA,
        )
    },
    partitions_def=partitions_def,  # Assign the partitions definition
)
def download_air_quality_map_pollutant_data(context: AssetExecutionContext) -> dict:
    """
    Download 'air quality map pollutant concentration distribution' data for the most recent year.
    """

    indicator = context.partition_key

    # Only download data for the partition's indicator
    context.log.info(f"➡️ Downloading data for year {MOST_RECENT_YEAR}")
    context.log.info(f"➡️ Downloading data for {indicator}")

    def fetch_single_pollutant():
        maps = {}
        maps["indicator"] = fetch_map_pollutant_concentration_distribution(
            year=MOST_RECENT_YEAR,
            indicatorType=INDICATOR_TYPE,
            indicator=indicator,
        )
        maps["year"] = MOST_RECENT_YEAR
        return maps

    return download_data(
        context=context,
        fetch_function=fetch_single_pollutant,
        asset_key="download_air_quality_map_pollutant_data",
    )

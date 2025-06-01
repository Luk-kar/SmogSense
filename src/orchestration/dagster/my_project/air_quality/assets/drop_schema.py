"""
Module contains assets to drop schema and its tables in the database.
"""

# Dagster
from dagster import AssetExecutionContext, asset

# Common
from common.constants import get_metadata_categories
from common.utils.database.schema_operations import (
    remove_schema_with_cascade,
)

# ORM models
from air_quality.models.annual_statistics_models import (
    SCHEMA_NAME as SCHEMA_ANNUAL_STATISTICS,
)
from air_quality.models.map_pollution_models import SCHEMA_NAME as SCHEMA_MAP_POLLUTION
from air_quality.models.sensor_models import SCHEMA_NAME as SCHEMA_SENSOR
from air_quality.models.station_models import SCHEMA_NAME as SCHEMA_STATION
from air_quality.models.unification_models import SCHEMA_NAME as SCHEMA_UNIFICATION

# AIR QUALITY
from air_quality.assets.constants import AirQualityAssetCategories as Categories, Groups


@asset(
    group_name=Groups.DATABASE_DROP_SCHEMA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DROP_SCHEMA,
            Categories.DATABASE,
        )
    },
)
def drop_schema_air_quality_map_pollution(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """
    remove_schema_with_cascade(context, SCHEMA_MAP_POLLUTION)


@asset(
    group_name=Groups.DATABASE_DROP_SCHEMA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DROP_SCHEMA,
            Categories.DATABASE,
        )
    },
)
def drop_schema_air_quality_annual_statistics(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """
    remove_schema_with_cascade(context, SCHEMA_ANNUAL_STATISTICS)


@asset(
    group_name=Groups.DATABASE_DROP_SCHEMA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DROP_SCHEMA,
            Categories.DATABASE,
        )
    },
)
def drop_schema_air_quality_sensor(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """
    remove_schema_with_cascade(context, SCHEMA_SENSOR)


@asset(
    group_name=Groups.DATABASE_DROP_SCHEMA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DROP_SCHEMA,
            Categories.DATABASE,
        )
    },
)
def drop_schema_air_quality_station(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """
    remove_schema_with_cascade(context, SCHEMA_STATION)


@asset(
    group_name=Groups.DATABASE_DROP_SCHEMA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DROP_SCHEMA,
            Categories.DATABASE,
        )
    },
)
def drop_schema_air_quality_unification(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """
    remove_schema_with_cascade(context, SCHEMA_UNIFICATION)

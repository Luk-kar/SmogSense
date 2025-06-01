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
from health.models.health_models import SCHEMA_NAME

# Health
from health.constants import HealthGroups, HealthAssetCategories as Categories


@asset(
    group_name=HealthGroups.DATABASE_DROP_SCHEMA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATABASE,
            Categories.DROP_SCHEMA,
        )
    },
)
def drop_schema_health_and_its_tables(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """

    remove_schema_with_cascade(context, SCHEMA_NAME)

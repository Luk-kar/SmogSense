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

# Pipeline
from territory.models import (
    SCHEMA_NAME as SCHEMA_TERRITORY,
)
from territory.assets.constants import (
    TerritoryAssetCategories as Categories,
    Groups as TerritoryGroups,
)


@asset(
    group_name=TerritoryGroups.DATABASE_DROP_SCHEMA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DROP_SCHEMA,
            Categories.DATABASE,
        )
    },
)
def drop_schema_territory(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """
    remove_schema_with_cascade(context, SCHEMA_TERRITORY)

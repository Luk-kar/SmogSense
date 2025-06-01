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
from social_media.models import SCHEMA_NAME

# AIR QUALITY
from social_media.assets.constants import (
    SocialMediaAssetCategories as Categories,
    Groups,
)


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
def drop_schema_social_media(context: AssetExecutionContext):
    """
    Drop the schema and its tables in the database using DROP SCHEMA IF EXISTS <schema> CASCADE.
    """
    remove_schema_with_cascade(context, SCHEMA_NAME)

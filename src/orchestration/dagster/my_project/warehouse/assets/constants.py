"""
Defines categories, groups, and utility functions to organize and manage metadata
for assets in the Dagster framework. It includes classifications specific to social media
data pipelines, such as categories for data acquisition, processing, and database operations.
The platform is called X, but for the project we will use the formal name Twitter.
"""

from common.constants import BaseAssetCategories, BaseGroups


class WarehouseCategories(BaseAssetCategories):
    """
    Extends the base asset categories with warehouse-specific ones.
    """

    WAREHOUSE = "warehouse"
    DATABASE = "database"
    DATABASE_BACKUP = "database_backup"
    DATABASE_RESTORE = "database_restore"
    DATABASE_UPLOAD = "database_upload"
    DATABASE_DROP_SCHEMA = "database_drop_schema"

    HEALTH_POLLUTION = "health_pollution"
    SOCIAL_MEDIA = "social_media"
    POLLUTION = "pollution"
    VIEW = "view"

    MINIO = "minio"
    EXAMPLE_DATA = "example_data"


_VIEWS = "_views"


class Groups(BaseGroups):
    """
    Extends the base groups for organizing air quality data pipelines.
    """

    HEALTH = "health" + _VIEWS
    POLLUTION = "pollution" + _VIEWS
    SOCIAL_MEDIA = "social_media" + _VIEWS
    EXAMPLE_PROJECT_DATA = "example_project_data"

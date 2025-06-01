"""
Defines categories, groups, and utility functions to organize and manage metadata 
for assets in the Dagster framework. It includes classifications specific to social media
data pipelines, such as categories for data acquisition, processing, and database operations.
The platform is called X, but for the project we will use the formal name Twitter.
"""

from common.constants import BaseAssetCategories, BaseGroups


class TerritoryAssetCategories(BaseAssetCategories):
    """
    Extends the base asset categories with air-quality-specific ones.
    """

    TERRITORY = "territory"
    DROP_SCHEMA = "drop_schema"
    JSONB = "jsonb"


class Groups(BaseGroups):
    """
    Extends the base groups for organizing air quality data pipelines.
    """


TERRITORY_DATA_EXTENSION = "_territory_data"


class TerritoryGroups:
    """
    Extends Groups with station-specific classifications for organizing data pipelines.
    """

    DATA_ACQUISITION = Groups.DATA_ACQUISITION + TERRITORY_DATA_EXTENSION
    DATA_PROCESSING = Groups.DATA_PROCESSING + TERRITORY_DATA_EXTENSION
    DATALAKE = Groups.DATALAKE + TERRITORY_DATA_EXTENSION
    DATABASE_UPLOAD = Groups.DATABASE_UPLOAD + TERRITORY_DATA_EXTENSION
    DROP_SCHEMA = Groups.DATABASE_DROP_SCHEMA + TERRITORY_DATA_EXTENSION

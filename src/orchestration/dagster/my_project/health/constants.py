"""
Defines categories, groups, and utility functions to organize and manage metadata 
for health-related assets in the Dagster framework, leveraging common constants.
"""

from common.constants import BaseAssetCategories, BaseGroups


class HealthGroups(BaseGroups):
    """
    Extends the base categories with health-specific ones.
    """

    HEALTH_DATA = "health_data"


HEALTH_DATA_EXTENSION = "_health_data"


class HealthAssetCategories:
    """
    Defines groups for organizing health data pipelines.
    """

    DATA_ACQUISITION = BaseAssetCategories.DATA_ACQUISITION + HEALTH_DATA_EXTENSION
    DATALAKE = BaseAssetCategories.DATALAKE + HEALTH_DATA_EXTENSION
    DATA_PROCESSING = BaseAssetCategories.DATA_PROCESSING + HEALTH_DATA_EXTENSION
    DATABASE = BaseAssetCategories.DATABASE + HEALTH_DATA_EXTENSION
    DATABASE_UPLOAD = BaseAssetCategories.DATABASE_UPLOAD + HEALTH_DATA_EXTENSION
    DATABASE_INIT_TABLE = (
        BaseAssetCategories.DATABASE_INIT_TABLE + HEALTH_DATA_EXTENSION
    )
    DATABASE_NORMALIZED = (
        BaseAssetCategories.DATABASE_NORMALIZED + HEALTH_DATA_EXTENSION
    )
    STAGING = BaseAssetCategories.STAGING + HEALTH_DATA_EXTENSION
    DATA_MODELING = BaseAssetCategories.DATA_MODELING + HEALTH_DATA_EXTENSION
    MEASUREMENT = "measurement" + HEALTH_DATA_EXTENSION
    DEATH_ILLNESS = "death_illness" + HEALTH_DATA_EXTENSION
    PROVINCE = "province" + HEALTH_DATA_EXTENSION
    HEALTH_DATA = "health_data"
    DROP_SCHEMA = "drop_schema" + HEALTH_DATA_EXTENSION
    DEMOGRAPHIC = "demographic" + HEALTH_DATA_EXTENSION
    COUNTRY = "country" + HEALTH_DATA_EXTENSION
    PROVINCE = "province" + HEALTH_DATA_EXTENSION

"""
Defines categories, groups, and utility functions to organize and manage metadata 
for assets in the Dagster framework. It includes classifications specific to social media
data pipelines, such as categories for data acquisition, processing, and database operations.
The platform is called X, but for the project we will use the formal name Twitter.
"""

from common.constants import BaseAssetCategories, BaseGroups


class SocialMediaAssetCategories(BaseAssetCategories):
    """
    Extends the base asset categories with air-quality-specific ones.
    """

    SOCIAL_MEDIA = "air_quality"
    TWEET_DATA = "tweet_data"
    TWEET_TABLE = "tweet_table"
    ENGAGEMENT_TABLE = "engagement_table"
    USER_TABLE = "user_table"
    BOUNDING_BOX_TABLE = "bounding_box_table"
    PLACE_TABLE = "place_table"
    HASHTAG_TABLE = "hashtag_table"
    TWEET_HASHTAG_TABLE = "tweet_hashtag_table"
    DATABASE_INIT_TABLE = "database_init_table"
    DATABASE_UPDATE_CONSTRAINTS = "database_update_constraints"
    DATABASE_NORMALIZED = "database_normalized"
    DROP_SCHEMA = "drop_schema"


class Groups(BaseGroups):
    """
    Extends the base groups for organizing air quality data pipelines.
    """


SOCIAL_MEDIA_DATA_EXTENSION = "social_media_data"


class StationGroups:
    """
    Extends Groups with station-specific classifications for organizing data pipelines.
    """

    DATA_ACQUISITION = Groups.DATA_ACQUISITION + SOCIAL_MEDIA_DATA_EXTENSION
    DATA_PROCESSING = Groups.DATA_PROCESSING + SOCIAL_MEDIA_DATA_EXTENSION
    DATALAKE = Groups.DATALAKE + SOCIAL_MEDIA_DATA_EXTENSION
    DATABASE_UPLOAD = Groups.DATABASE_UPLOAD + SOCIAL_MEDIA_DATA_EXTENSION
    DROP_SCHEMA = Groups.DATABASE_DROP_SCHEMA + SOCIAL_MEDIA_DATA_EXTENSION

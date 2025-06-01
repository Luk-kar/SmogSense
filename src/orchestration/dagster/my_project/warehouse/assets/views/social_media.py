
"""
Contains the assets for views related to  in the warehouse.
"""

# Pipelines
from warehouse.assets.constants import (
    WarehouseCategories as Categories,
    Groups,
)
import warehouse.sql.views.social_media as sql_views
from warehouse.assets.utils import get_module_path, execute_sql_view_creation

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)


DAILY_TWEET_VOLUME_TREND_VIEW = get_module_path(sql_views) / "daily_tweet_volume_trend.sql"
MONTHLY_TWEET_VOLUME_TREND_VIEW = get_module_path(sql_views) / "monthly_tweet_volume_trend.sql"
MOST_ACTIVE_USERS_VIEW = get_module_path(sql_views) / "most_active_users.sql"
MOST_ENGAGED_HASHTAGS_VIEW = get_module_path(sql_views) / "most_engaged_hashtags.sql"
MOST_ENGAGED_TWEETS_ON_POLLUTION_HASHTAGS_VIEW = get_module_path(sql_views) / "most_engaged_tweets_on_pollution_hashtags.sql"
TWEET_COUNT_BY_POLLUTION_HASHTAGS_VIEW = get_module_path(sql_views) / "tweet_count_by_pollution_hashtags.sql"

@asset(
    group_name=Groups.SOCIAL_MEDIA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(DAILY_TWEET_VOLUME_TREND_VIEW),
    },
)
def view_daily_tweet_volume_trend(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, DAILY_TWEET_VOLUME_TREND_VIEW)

@asset(
    group_name=Groups.SOCIAL_MEDIA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(MONTHLY_TWEET_VOLUME_TREND_VIEW),
    },
)
def view_monthly_tweet_volume_trend(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, MONTHLY_TWEET_VOLUME_TREND_VIEW)

@asset(
    group_name=Groups.SOCIAL_MEDIA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(MOST_ACTIVE_USERS_VIEW),
    },
)
def view_most_active_users(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, MOST_ACTIVE_USERS_VIEW)

@asset(
    group_name=Groups.SOCIAL_MEDIA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(MOST_ENGAGED_HASHTAGS_VIEW),
    },
)
def view_most_engaged_hashtags(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, MOST_ENGAGED_HASHTAGS_VIEW)

@asset(
    group_name=Groups.SOCIAL_MEDIA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(MOST_ENGAGED_TWEETS_ON_POLLUTION_HASHTAGS_VIEW),
    },
)
def view_most_engaged_tweets_on_pollution_hashtags(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, MOST_ENGAGED_TWEETS_ON_POLLUTION_HASHTAGS_VIEW)

@asset(
    group_name=Groups.SOCIAL_MEDIA,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(TWEET_COUNT_BY_POLLUTION_HASHTAGS_VIEW),
    },
)
def view_tweet_count_by_pollution_hashtags(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, TWEET_COUNT_BY_POLLUTION_HASHTAGS_VIEW)


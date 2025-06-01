"""
Contains asset checks for validating the consistency and structure 
of data between Pandas DataFrames and PostgreSQL database tables, 
leveraging Dagster and SQLAlchemy. 
It includes functions for comparing row counts, column schemas, 
and data types to ensure data integrity. 
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetIn,
    AssetCheckExecutionContext,
    AssetKey,
    asset_check,
)

# Pipeline
from social_media.models import (
    Tweet,
    User,
    Engagement,
    Place,
    BoundingBox,
    Hashtag,
    HashtagTweet,
)
# fmt: off
from social_media.assets.database_upload import (
    upload_data_tweet,
    upload_data_user,
    upload_data_engagement,
    upload_data_place,
    upload_data_bounding_box,
    upload_data_hashtag,
    upload_data_tweet_hashtag,
)
# fmt: on
from common.utils.database.data_validation import (
    compare_uploaded_database_data,
)


@asset_check(
    asset=upload_data_tweet,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_tweet": AssetIn(key=AssetKey("create_dataframe_tweet"))
    },
)
def check_tweet_data(
    context: AssetCheckExecutionContext,
    create_dataframe_tweet: pd.DataFrame,
):
    """Checks if 'tweet' data matches the data in the database."""

    return compare_uploaded_database_data(context, create_dataframe_tweet, Tweet)


@asset_check(
    asset=upload_data_user,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_user": AssetIn(key=AssetKey("create_dataframe_user"))
    },
)
def check_user_data(
    context: AssetCheckExecutionContext,
    create_dataframe_user: pd.DataFrame,
):
    """Asset check for 'user' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_user, User)


@asset_check(
    asset=upload_data_engagement,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_engagement": AssetIn(
            key=AssetKey("create_dataframe_engagement")
        )
    },
)
def check_engagement_data(
    context: AssetCheckExecutionContext,
    create_dataframe_engagement: pd.DataFrame,
):
    """Asset check for 'engagement' data uploaded to the database."""

    return compare_uploaded_database_data(
        context, create_dataframe_engagement, Engagement
    )


@asset_check(
    asset=upload_data_place,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_place": AssetIn(key=AssetKey("create_dataframe_place"))
    },
)
def check_place_data(
    context: AssetCheckExecutionContext,
    create_dataframe_place: pd.DataFrame,
):
    """Asset check for 'place' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_place, Place)


@asset_check(
    asset=upload_data_bounding_box,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_bounding_box": AssetIn(
            key=AssetKey("create_dataframe_bounding_box")
        )
    },
)
def check_bounding_box_data(
    context: AssetCheckExecutionContext,
    create_dataframe_bounding_box: pd.DataFrame,
):
    """Asset check for 'bounding_box' data uploaded to the database."""

    return compare_uploaded_database_data(
        context, create_dataframe_bounding_box, BoundingBox
    )


@asset_check(
    asset=upload_data_hashtag,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_hashtag": AssetIn(key=AssetKey("create_dataframe_hashtag"))
    },
)
def check_hashtag_data(
    context: AssetCheckExecutionContext,
    create_dataframe_hashtag: pd.DataFrame,
):
    """Asset check for 'hashtag' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_hashtag, Hashtag)


@asset_check(
    asset=upload_data_tweet_hashtag,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_tweet_hashtag": AssetIn(
            key=AssetKey("create_dataframe_tweet_hashtag")
        )
    },
)
def check_tweet_hashtag_data(
    context: AssetCheckExecutionContext,
    create_dataframe_tweet_hashtag: pd.DataFrame,
):
    """Asset check for 'tweet_hashtag' data uploaded to the database."""

    return compare_uploaded_database_data(
        context, create_dataframe_tweet_hashtag, HashtagTweet
    )

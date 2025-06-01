"""
Contains the assets for data processing of the 'social media' data.
"""

# Python
from typing import Any

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)

# Pipeline
from social_media.assets.constants import (
    SocialMediaAssetCategories as Categories,
    Groups as SocialMediaGroups,
)
from common.constants import get_metadata_categories
from common.utils.dataframe import (
    convert_to_dataframe,
)
from common.utils.validation import (
    log_data_type_and_validate_if_list_or_dict,
)
from common.utils.logging import (
    log_columns_statistics,
)


@asset(
    group_name=SocialMediaGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATA_PROCESSING,
            Categories.DATA_PROCESSING,
        )
    },
)
def flatten_and_extract_social_media_statistics_data(
    context: AssetExecutionContext,
    download_social_media_data_from_minio: Any,
) -> dict[str, pd.DataFrame]:
    """
    Transforms downloaded 'social media statistics' data into multiple DataFrames
    following the structure laid out in the schema models.
    Returns a dictionary where each key is a table name and each value is a DataFrame.
    """

    data = download_social_media_data_from_minio
    log_data_type_and_validate_if_list_or_dict(context, data)

    # Containers to accumulate row data:

    entries = {
        "tweet": [],
        "engagement": [],
        "user": [],
        "hashtag": [],
        "tweet_hashtag": [],
        "place": [],
        "bounding_box": [],
    }

    for tweet_json in data:

        # Tweet table
        # Extract IDs for tweet and user
        tweet_id = tweet_json["ids"]["id_tweet"]
        user_id = tweet_json["ids"]["id_user"]

        # Extract place data to match with the id_place
        place = None
        if "place" in tweet_json and tweet_json["place"]:

            place = tweet_json["place"]

        # Tweet table
        place_keys = [
            "full_name",
            "country",
            "country_code",
            "place_name",
            "place_type",
        ]

        entries["tweet"].append(
            {
                "tweet_id": tweet_id,
                "user_id": user_id,
                "text": tweet_json["text"],
                "created_at": tweet_json["created_at"],
                # Unpacking place data to simplify
                # the further matching with the id_place
                **{key: place.get(key) if place else None for key in place_keys},
                ("coordinates"): (
                    place["bounding_box"]["coordinates"] if place else None
                ),
            }
        )

        # Engagement table
        engagement_data = tweet_json["engagement"]
        entries["engagement"].append(
            {
                "tweet_id": tweet_id,
                "like_count": int(engagement_data["like_count"]),
                "retweet_count": int(engagement_data["retweet_count"]),
                "quote_count": int(engagement_data["quote_count"]),
                "reply_count": int(engagement_data["reply_count"]),
                "view_count": int(engagement_data["view_count"]),
            }
        )

        # User table
        user_data = tweet_json["user"]

        entries["user"].append(
            {
                "user_id": user_id,
                "favourites_count": user_data["favourites_count"],
                "followers_count": user_data["followers_count"],
                "listed_count": user_data["listed_count"],
                "tweets_count": user_data["tweets_count"],
                "is_verified_paid_blue": user_data["is_verified_paid_blue"],
                "is_verified_unpaid": user_data["is_verified_unpaid"],
            }
        )

        # Hashtag table
        for hashtag in tweet_json.get("hashtags", []):
            if hashtag not in entries["hashtag"]:
                entries["hashtag"].append({"hashtag": hashtag})

        # Tweet-Hashtag table
        for hashtag in tweet_json.get("hashtags", []):
            entries["tweet_hashtag"].append({"tweet_id": tweet_id, "hashtag": hashtag})

        # Place table
        if place:
            entries["place"].append(
                {
                    **{key: place.get(key) for key in place_keys},
                    "centroid": place["centroid"],
                    "coordinates": place["bounding_box"]["coordinates"],
                }
            )

            # Bounding Box table
            entries["bounding_box"].append(
                {
                    "coordinates": place["bounding_box"]["coordinates"],
                    "type": place["bounding_box"]["type"],
                }
            )

    for table, table_rows in entries.items():

        df = convert_to_dataframe(context, table_rows)
        entries[table] = df

    for table, table_df in entries.items():

        context.log.info(f"➡️ {table}")
        log_columns_statistics(context, table_df)

    return entries

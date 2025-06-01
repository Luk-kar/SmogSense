"""
Data modeling assets for the 'social media' data.
"""

# Python
import json
from typing import Dict

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    Failure,
    asset,
)


# Local
from common.utils.logging import (
    log_asset_materialization,
    log_dataframe_info,
)
from common.constants import get_metadata_categories
from common.utils.geometry import convert_to_wkt
from social_media.assets.constants import (
    SocialMediaAssetCategories as Categories,
    Groups as SocialMediaGroups,
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
def create_dataframe_tweet(
    context: AssetExecutionContext,
    flatten_and_extract_social_media_statistics_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Creates 'tweet' DataFrame from the dictionary output of
    'flatten_and_extract_social_media_statistics_data'.
    'place' column serves as a foreign key 'id_place' placeholder to the 'place' table.
    """
    try:
        df_source = flatten_and_extract_social_media_statistics_data["tweet"]

        log_nulls_in_dataframe(context, df_source)

        log_dataframe_info(context, df_source, "tweets source")

        df_tweet = df_source.drop_duplicates(subset=["tweet_id"])

        for column in ["tweet_id", "user_id"]:
            log_values_with_leading_zeros(context, df_tweet, column)

        df_tweet["created_at"] = pd.to_datetime(
            df_tweet["created_at"],
            format="%a %b %d %H:%M:%S %z %Y",  # Format based on the provided example
            errors="coerce",
        )

        # Convert bounding_box to WKT format to match the 'id_bounding_box'
        # column in the 'place' table
        mask = df_tweet["coordinates"].notna()
        df_tweet.loc[mask, "coordinates"] = df_tweet.loc[mask, "coordinates"].apply(
            convert_to_wkt
        )

        df_tweet["day_of_week"] = df_tweet["created_at"].dt.weekday.astype("int8") + 1

        df_tweet["month"] = df_tweet["created_at"].dt.month.astype("int8")

        for column in ["tweet_id", "user_id"]:
            df_tweet[column] = df_tweet[column].astype("int64")

        # Log max values for `"tweet_id"``, `"user_id"`
        # to check if they are within the bigint_range
        # https://www.postgresql.org/docs/current/datatype-numeric.html
        bigint_range = (-9223372036854775808, 9223372036854775807)
        for column in ["tweet_id", "user_id"]:
            is_within_range = df_tweet[column].between(*bigint_range).all()

            if not is_within_range:
                raise ValueError(
                    f"Values in the column '{column}' are not within the bigint range."
                )
            else:
                context.log.info(
                    f"✅ Values in the column '{column}' are within the bigint range."
                )

        validate_non_negative_values(
            df_tweet,
            ["tweet_id", "user_id", "day_of_week", "month"],
        )

        df_tweet = transform_id_suffixes_to_prefixes_in_column_names(context, df_tweet)

        # Rename columns from plural to singular
        df_tweet.rename(
            columns={
                "favourites_count": "favourite_count",
                "followers_count": "follower_count",
                "tweets_count": "tweet_count",
            },
            inplace=True,
        )

        log_asset_materialization(
            context=context,
            data_frame=df_tweet,
            asset_key="create_dataframe_tweet",
            description="Tweet DataFrame created",
        )

        return df_tweet

    except Exception as e:
        raise Failure(f"Failed to create 'tweet' DataFrame: {e}") from e


@asset(
    group_name=SocialMediaGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATA_PROCESSING,
            Categories.DATA_MODELING,
        )
    },
)
def create_dataframe_user(
    context: AssetExecutionContext,
    flatten_and_extract_social_media_statistics_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Creates 'user' DataFrame from the dictionary output.
    """
    try:
        df_source = flatten_and_extract_social_media_statistics_data["user"]

        log_dataframe_info(context, df_source, "users source")

        log_nulls_in_dataframe(context, df_source)

        df_user = df_source.drop_duplicates(subset=["user_id"])

        df_user["user_id"] = df_user["user_id"].astype("int64")

        validate_non_negative_values(
            df_user,
            [
                "user_id",
                "favourites_count",
                "followers_count",
                "listed_count",
                "tweets_count",
            ],
        )

        # Rename columns from plural to singular
        df_user.rename(
            columns={
                "favourites_count": "favourite_count",
                "followers_count": "follower_count",
                "tweets_count": "tweet_count",
            },
            inplace=True,
        )

        df_user = transform_id_suffixes_to_prefixes_in_column_names(context, df_user)

        context.log.info(f"'user' DataFrame created successfully.\n{df_user.head(3)}")

        # Log final
        log_asset_materialization(
            context=context,
            data_frame=df_user,
            asset_key="create_dataframe_user",
            description="User DataFrame created",
        )

        return df_user

    except Exception as e:
        raise Failure(f"Failed to create 'user' DataFrame: {e}") from e


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
def create_dataframe_engagement(
    context: AssetExecutionContext,
    flatten_and_extract_social_media_statistics_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Creates 'engagement' DataFrame from the dictionary output of
    'flatten_and_extract_social_media_statistics_data'.
    """
    try:
        df_source = flatten_and_extract_social_media_statistics_data["engagement"]

        log_dataframe_info(context, df_source, "engagements source")

        log_nulls_in_dataframe(context, df_source)

        validate_non_negative_values(
            df_source,
            ["like_count", "retweet_count", "quote_count", "reply_count", "view_count"],
        )

        df_engagement = df_source.drop_duplicates(subset=["tweet_id"])

        df_engagement["tweet_id"] = df_engagement["tweet_id"].astype("int64")

        df_engagement = transform_id_suffixes_to_prefixes_in_column_names(
            context, df_engagement
        )

        context.log.info(
            f"'engagement' DataFrame created successfully.\n{df_engagement.head(3)}"
        )

        log_asset_materialization(
            context=context,
            data_frame=df_engagement,
            asset_key="create_dataframe_engagement",
            description="Engagement DataFrame created",
        )

        return df_engagement

    except Exception as e:
        raise Failure(f"Failed to create 'engagement' DataFrame: {e}") from e


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
def create_dataframe_hashtag(
    context: AssetExecutionContext,
    flatten_and_extract_social_media_statistics_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Creates 'hashtag' DataFrame from the dictionary output of
    'flatten_and_extract_social_media_statistics_data'.
    """
    try:
        df_source = flatten_and_extract_social_media_statistics_data["hashtag"]

        log_dataframe_info(context, df_source, "hashtags source")

        log_nulls_in_dataframe(context, df_source)

        df_hashtag = df_source.drop_duplicates(subset=["hashtag"]).reset_index(
            drop=True
        )

        df_hashtag.rename(columns={"hashtag": "hashtag_name"}, inplace=True)

        context.log.info(
            f"'hashtag' DataFrame created successfully.\n{df_hashtag.head(3)}"
        )

        log_asset_materialization(
            context=context,
            data_frame=df_hashtag,
            asset_key="create_dataframe_hashtag",
            description="Hashtag DataFrame created",
        )

        return df_hashtag

    except Exception as e:
        raise Failure(f"Failed to create 'hashtag' DataFrame: {e}") from e


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
def create_dataframe_tweet_hashtag(
    context: AssetExecutionContext,
    flatten_and_extract_social_media_statistics_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Creates 'tweet_hashtag' DataFrame from the dictionary output of
    'flatten_and_extract_social_media_statistics_data'.
    Many-to-many bridge table linking tweets and hashtags.
    'hashtag_name' column serves as a foreign key placeholder 'id_hashtag' to the 'hashtag' table.
    """
    try:
        df_source = flatten_and_extract_social_media_statistics_data["tweet_hashtag"]

        log_dataframe_info(context, df_source, "tweet_hashtags source")

        log_nulls_in_dataframe(context, df_source)

        df_tweet_hashtag = df_source.drop_duplicates().reset_index(drop=True)

        df_tweet_hashtag["tweet_id"] = df_tweet_hashtag["tweet_id"].astype("int64")

        # Serves as a foreign key placeholder to the 'hashtag' table
        df_tweet_hashtag.rename(columns={"hashtag": "hashtag_name"}, inplace=True)

        df_tweet_hashtag = transform_id_suffixes_to_prefixes_in_column_names(
            context, df_tweet_hashtag
        )

        context.log.info(
            f"'tweet_hashtag' DataFrame created successfully.\n{df_tweet_hashtag.head(3)}"
        )

        log_asset_materialization(
            context=context,
            data_frame=df_tweet_hashtag,
            asset_key="create_dataframe_tweet_hashtag",
            description="Tweet-Hashtag DataFrame created",
        )

        return df_tweet_hashtag

    except Exception as e:
        raise Failure(f"Failed to create 'tweet_hashtag' DataFrame: {e}") from e


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
def create_dataframe_place(
    context: AssetExecutionContext,
    flatten_and_extract_social_media_statistics_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Creates 'place' DataFrame from the dictionary output of
    'flatten_and_extract_social_media_statistics_data'.
    'coordinates' column serves as a foreign key 'id_bounding_box' placeholder
    to the 'bounding_box' table.
    """
    try:
        df_source = flatten_and_extract_social_media_statistics_data["place"]

        log_dataframe_info(context, df_source, "place source")

        log_nulls_in_dataframe(context, df_source)

        df_place = remove_duplicates_with_stringified_dicts(df_source)

        # Convert bounding_box to WKT format to match the 'id_bounding_box'
        # column in the 'bounding box' table
        df_place["coordinates"] = df_place["coordinates"].apply(convert_to_wkt)

        context.log.info(f"'place' DataFrame created successfully.\n{df_place.head(3)}")

        log_asset_materialization(
            context=context,
            data_frame=df_place,
            asset_key="create_dataframe_place",
            description="Place DataFrame created",
        )

        return df_place

    except Exception as e:
        raise Failure(f"Failed to create 'place' DataFrame: {e}") from e


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
def create_dataframe_bounding_box(
    context: AssetExecutionContext,
    flatten_and_extract_social_media_statistics_data: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Creates 'bounding_box' DataFrame from the dictionary output of
    'flatten_and_extract_social_media_statistics_data'.
    """
    try:
        df_source = flatten_and_extract_social_media_statistics_data["bounding_box"]

        log_dataframe_info(context, df_source, "bounding_box source")

        log_nulls_in_dataframe(context, df_source)

        df_bounding_box = remove_duplicates_with_stringified_dicts(df_source)

        df_bounding_box["coordinates"] = df_bounding_box["coordinates"].apply(
            convert_to_wkt
        )

        context.log.info(
            f"'bounding_box' DataFrame created successfully.\n{df_bounding_box.head(3)}"
        )

        log_asset_materialization(
            context=context,
            data_frame=df_bounding_box,
            asset_key="create_dataframe_bounding_box",
            description="BoundingBoxes DataFrame created",
        )

        return df_bounding_box

    except Exception as e:
        raise Failure(f"Failed to create 'bounding_box' DataFrame: {e}") from e


def remove_duplicates_with_stringified_dicts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts dictionary columns to JSON strings and removes duplicate rows
    by creating a temporary string-based comparison column.
    """
    # Convert dictionary columns to JSON strings to allow string-based duplicate removal
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            df[col] = df[col].apply(
                lambda x: json.dumps(x, sort_keys=True) if isinstance(x, dict) else x
            )

    # Create a temporary column for string-based comparison across all columns
    df["stringified_row"] = df.apply(lambda row: "|".join(row.astype(str)), axis=1)

    # Drop duplicates based on the stringified representation
    df_cleaned = df.drop_duplicates(subset=["stringified_row"]).reset_index(drop=True)

    # Drop the temporary string column after deduplication
    df_cleaned.drop(columns=["stringified_row"], inplace=True)

    return df_cleaned


def transform_id_suffixes_to_prefixes_in_column_names(
    context: AssetExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Renames columns where suffix '_id' appears at the end to 'id_' prefix and logs
    the changes side by side.
    """

    # Create a mapping of column names before and after renaming
    rename_mapping = {
        col: f"id_{col[:-3]}" for col in df.columns if col.endswith("_id")
    }

    # Log before and after side by side
    if rename_mapping:
        context.log.info("🔄 Renaming columns (before -> after):")

        renamed_list = []
        for old_col, new_col in rename_mapping.items():
            renamed_list.append(f"    {old_col} -> {new_col}")

        context.log.info("\n".join(renamed_list))

    # Perform renaming
    df_renamed = df.rename(columns=rename_mapping)

    # Log the renamed DataFrame columns
    context.log.info(f"✅ Columns after renaming: {df_renamed.columns.tolist()}")

    return df_renamed


def log_values_with_leading_zeros(
    context: AssetExecutionContext, df: pd.Series, column_name: str
):
    """
    Logs the string column values with leading zeros.
    """

    column = df[column_name]

    df_leading_zeros = column[column.str.startswith("0")]
    if not df_leading_zeros.empty:
        context.log.warning(
            f"⚠️ Found {len(df_leading_zeros)} {column_name}"
            f"with leading zeros:\n{df_leading_zeros[column_name].tolist()}"
        )


def log_nulls_in_dataframe(context: AssetExecutionContext, df: pd.DataFrame):
    """
    Logs the number of nulls in each column of the DataFrame.
    """

    for column in df.columns:
        nulls_count = df[column].isnull().sum()

        if nulls_count > 0:
            context.log.warning(f"⚠️ Nulls in the column '{column}': {nulls_count}")


def validate_non_negative_values(df: pd.DataFrame, column_names: list[str]):
    """
    Validates if the values in the specified columns are non-negative.
    """

    for column in column_names:
        lower_than_0_count = df[column].lt(0).sum()

        if lower_than_0_count > 0:

            raise ValueError(
                "⚠️ Values lower than 0 in the column\n"
                f"'{column}': {lower_than_0_count}"
            )

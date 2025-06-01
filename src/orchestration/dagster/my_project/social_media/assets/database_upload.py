"""
Uploads the modeled social_media DataFrames into the PostgreSQL database
using the SQLAlchemy ORM models defined in `models/__init__.py`.

Following a similar pattern to the air_quality example, each table is
uploaded in a sequence that respects foreign-key dependencies:
1) bounding_box
2) place  (FK -> bounding_box)
3) user   (no FK dependencies)
4) hashtag
5) tweet  (FK -> user, place)
6) engagement (FK -> tweet)
7) tweet_hashtag (FK -> tweet, hashtag)
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetKey,
    asset,
)

# MySQLAlchemy
from sqlalchemy.sql import func

# Pipeline
from social_media.models import (
    BoundingBox,
    Place,
    User,
    Hashtag,
    Tweet,
    Engagement,
    HashtagTweet,
)
from social_media.assets.constants import (
    SocialMediaAssetCategories as Categories,
    Groups as SocialMediaGroups,
)
from common.constants import get_metadata_categories
from common.utils.database.data_ingestion import (
    upload_data_and_log_materialization,
)
from common.utils.database.session_handling import get_database_session
from common.utils.database.data_preprocessing import (
    map_foreign_keys_general,
)
from common.utils.logging import log_dataframe_info


@asset(
    group_name=SocialMediaGroups.DATABASE_UPLOAD,  # or any relevant group name
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.BOUNDING_BOX_TABLE,  # or however you wish to categorize
        )
    },
)
def upload_data_bounding_box(
    context: AssetExecutionContext,
    create_dataframe_bounding_box: pd.DataFrame,
):
    """
    Upload 'bounding_box' data to PostgreSQL database using bulk operations.
    """

    log_dataframe_info(context, create_dataframe_bounding_box, "bounding_box")

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_bounding_box,
        model_class=BoundingBox,
        asset_key_str="upload_data_bounding_box",
        description="Uploaded 'bounding_box' data to PostgreSQL database.",
    )


@asset(
    group_name=SocialMediaGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    # place depends on bounding_box
    non_argument_deps={AssetKey("upload_data_bounding_box")},
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.PLACE_TABLE,
        )
    },
)
def upload_data_place(
    context: AssetExecutionContext,
    create_dataframe_place: pd.DataFrame,
):
    """
    Upload 'place' data to PostgreSQL database using bulk operations.
    This table references bounding_box (id_bounding_box).
    """
    # Example approach to map the bounding_box column -> existing bounding_box IDs
    # (Assumes create_dataframe_place has a column, e.g. "bounding_box",
    # which is a placeholder for the actual bounding_box ID.)

    log_dataframe_info(context, create_dataframe_place, "place")

    with get_database_session(context) as session:

        mapped_df = process_bounding_box_mapping(
            session, context, create_dataframe_place
        )

        context.log.info(
            f"Place DataFrame after mapping id_province:\n{mapped_df.head()}"
        )

        # Then upload the mapped data
        upload_data_and_log_materialization(
            context=context,
            data_frame=mapped_df,
            model_class=Place,
            asset_key_str="upload_data_place",
            description="Uploaded 'place' data to PostgreSQL database.",
        )


@asset(
    group_name=SocialMediaGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    # user has no FKs referencing other tables, so no non_argument_deps needed
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.USER_TABLE,  # example category
        )
    },
)
def upload_data_user(
    context: AssetExecutionContext,
    create_dataframe_user: pd.DataFrame,
):
    """
    Upload 'user' data to PostgreSQL database using bulk operations.
    """

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_user,
        model_class=User,
        asset_key_str="upload_data_user",
        description="Uploaded 'user' data to PostgreSQL database.",
        mode="update_non_id_values",  # to preserve id_user
    )


@asset(
    group_name=SocialMediaGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    # hashtag has no FKs referencing other tables, so no non_argument_deps needed
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.HASHTAG_TABLE,  # example category
        )
    },
)
def upload_data_hashtag(
    context: AssetExecutionContext,
    create_dataframe_hashtag: pd.DataFrame,
):
    """
    Upload 'hashtag' data to PostgreSQL database using bulk operations.
    """
    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_hashtag,
        model_class=Hashtag,
        asset_key_str="upload_data_hashtag",
        description="Uploaded 'hashtag' data to PostgreSQL database.",
    )


@asset(
    group_name=SocialMediaGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    # tweet depends on user and place
    non_argument_deps={AssetKey("upload_data_user"), AssetKey("upload_data_place")},
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.TWEET_TABLE,  # example category
        )
    },
)
def upload_data_tweet(
    context: AssetExecutionContext,
    create_dataframe_tweet: pd.DataFrame,
):
    """
    Upload 'tweet' data to PostgreSQL database using bulk operations.
    References user.id_user and place.id_place as foreign keys.
    """
    log_dataframe_info(context, create_dataframe_tweet, "tweet")

    # Columns used for mapping place_id
    place_columns = [
        "id_bounding_box",
        "country",
        "country_code",
        "full_name",
        "place_name",
        "place_type",
    ]

    with get_database_session(context) as session:

        df_tweet = process_bounding_box_mapping(
            session, context, create_dataframe_tweet
        )

        # Map df_tweet to place_id
        place_mapping = {
            tuple(getattr(place, col) for col in place_columns): place.id_place
            for place in session.query(Place).all()
        }

        df_tweet["id_place"] = df_tweet.apply(
            lambda row: place_mapping.get(
                tuple(row[col] for col in place_columns),
                None,
            ),
            axis=1,
        ).astype(pd.Int64Dtype())

        # Drop the
        # 'id_bounding_box', 'country', 'country_code',
        # 'full_name', 'place_name', 'place_type' columns
        df_tweet.drop(
            columns=place_columns,
            inplace=True,
        )

        # Log the row where id_place exists if any `id_place` is not null
        if df_tweet["id_place"].notnull().sum():

            context.log.info(
                "An example of tweet entry after mapping id_place:\n"
                f"{df_tweet[df_tweet['id_place'].notnull()].iloc[0]}"
            )

        else:
            context.log.info("No 'id_place' values were mapped.")

        upload_data_and_log_materialization(
            context=context,
            data_frame=df_tweet,
            model_class=Tweet,
            asset_key_str="upload_data_tweet",
            description="Uploaded 'tweet' data to PostgreSQL database.",
            mode="update_non_id_values",  # to preserve id_tweet
        )


@asset(
    group_name=SocialMediaGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    # engagement depends on tweet
    non_argument_deps={AssetKey("upload_data_tweet")},
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ENGAGEMENT_TABLE,  # example category
        )
    },
)
def upload_data_engagement(
    context: AssetExecutionContext,
    create_dataframe_engagement: pd.DataFrame,
):
    """
    Upload 'engagement' data to PostgreSQL database using bulk operations.
    References tweet.id_tweet as foreign key.
    """

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_engagement,
        model_class=Engagement,
        asset_key_str="upload_data_engagement",
        description="Uploaded 'engagement' data to PostgreSQL database.",
        mode="update_non_id_values",  # to preserve id_tweet
    )


@asset(
    group_name=SocialMediaGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    # tweet_hashtag depends on tweet and hashtag
    non_argument_deps={AssetKey("upload_data_tweet"), AssetKey("upload_data_hashtag")},
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.TWEET_HASHTAG_TABLE,  # example category
        )
    },
)
def upload_data_tweet_hashtag(
    context: AssetExecutionContext,
    create_dataframe_tweet_hashtag: pd.DataFrame,
):
    """
    Upload 'tweet_hashtag' data to PostgreSQL database using bulk operations.
    References tweet.id_tweet and hashtag.id_hashtag as foreign keys.
    """

    log_dataframe_info(context, create_dataframe_tweet_hashtag, "tweet_hashtag")

    with get_database_session(context) as session:

        # gather existing hashtags
        all_hashtags = session.query(Hashtag).all()
        hashtag_mapping = {h.hashtag_name: h.id_hashtag for h in all_hashtags}

        context.log.info(
            f"Hashtag mapping (first 50): {dict(list(hashtag_mapping.items())[:50])}"
        )

        mappings = {
            "hashtag_name": hashtag_mapping,
        }

        mapped_df = map_foreign_keys_general(
            create_dataframe_tweet_hashtag.copy(), mappings, context
        )

        # rename `id_hashtag_name` to `id_hashtag` to match the ORM model
        mapped_df.rename(columns={"id_hashtag_name": "id_hashtag"}, inplace=True)

        context.log.info(
            f"Tweet-Hashtag DataFrame after mapping id_hashtag:\n{mapped_df.head()}"
        )

        upload_data_and_log_materialization(
            context=context,
            data_frame=mapped_df,
            model_class=HashtagTweet,
            asset_key_str="upload_data_tweet_hashtag",
            description="Uploaded 'tweet_hashtag' data to PostgreSQL database.",
        )


def normalize_coordinates_format(coordinates_series: pd.Series) -> pd.Series:
    """
    Normalize coordinate strings by removing unnecessary spaces and
    ensuring consistent formatting.

    Args:
        coordinates_series (pd.Series): Pandas Series containing corrupted coordinate strings.

    Returns:
        pd.Series: Series with normalized coordinate strings.
    """
    return (
        coordinates_series.str.replace(
            r"\s*,\s*", ",", regex=True
        )  # Remove spaces around commas
        .str.replace(
            r"\s*\(\s*", "(", regex=True
        )  # Remove spaces before opening parentheses
        .str.replace(
            r"\s*\)\s*", ")", regex=True
        )  # Remove spaces before closing parentheses
    )


def process_bounding_box_mapping(session, context, create_dataframe):
    """
    Process and map bounding box coordinates to their corresponding IDs.

    Args:
        session: Database session to query bounding box data.
        context: AssetExecutionContext for logging and metadata.
        create_dataframe: DataFrame containing place data.

    Returns:
        pd.DataFrame: DataFrame with mapped bounding box IDs.
    """

    # Retrieve existing bounding boxes from DB
    all_bounding_boxes = session.query(
        BoundingBox.id_bounding_box,
        func.ST_AsText(BoundingBox.coordinates).label("coordinates"),
    ).all()

    bounding_boxes_mapping = {
        box.coordinates: box.id_bounding_box for box in all_bounding_boxes
    }

    context.log.info(f"Bounding box mapping: {bounding_boxes_mapping}")

    non_missing_coordinates = create_dataframe["coordinates"].notnull()

    if non_missing_coordinates.sum():

        context.log.info(
            f"Processing existing {non_missing_coordinates.sum()} coordinates..."
        )

        # log example coordinates
        example_coordinates = create_dataframe.loc[
            non_missing_coordinates, "coordinates"
        ].iloc[0]
        context.log.info(
            f"Example 'coordinates':\n{example_coordinates}\n"
            f"Type: {type(example_coordinates)}"
        )

        create_dataframe.loc[non_missing_coordinates, "coordinates"] = (
            normalize_coordinates_format(
                create_dataframe.loc[non_missing_coordinates, "coordinates"]
            )
        )

        mappings = {"coordinates": bounding_boxes_mapping}

        mapped_df = map_foreign_keys_general(
            create_dataframe.loc[non_missing_coordinates].copy(), mappings, context
        )

        # Rename id_coordinates to id_bounding_box to match the ORM model
        mapped_df.rename(columns={"id_coordinates": "id_bounding_box"}, inplace=True)

        # Add the values 'id_bounding_box' to the original DataFrame
        create_dataframe.loc[non_missing_coordinates, "id_bounding_box"] = (
            mapped_df.get("id_bounding_box", pd.NA)
        )
    else:
        # Ensure that rows without a mapping result remain as NaN in id_bounding_box
        create_dataframe["id_bounding_box"] = pd.NA

    # Drop the 'coordinates' column as it is no longer needed
    create_dataframe.drop(columns=["coordinates"], inplace=True)

    return create_dataframe

# Python
from dagster import asset, AssetExecutionContext
import pandas as pd

# Common
from common.constants import get_metadata_categories
from common.utils.logging import log_dataframe_info

# Pipeline
from models_deployment.assets.constants import AssetCategories, Groups


@asset(
    group_name=Groups.MODEL_TWITTER_ENGAGEMENT,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            AssetCategories.DATA_ACQUISITION,
            AssetCategories.SOCIAL_MEDIA,
            AssetCategories.TWITTER_ENGAGEMENT_PREDICTOR,
        )
    },
)
def extract_twitter_engagement_metrics(context: AssetExecutionContext) -> pd.DataFrame:
    """
    Query the database to extract tweets and their engagement metrics.
    """

    query = """
    SELECT t.text, 
        e.like_count, 
        e.retweet_count, 
        e.quote_count, 
        e.reply_count, 
        e.view_count
    FROM social_media_dim.tweet t
    JOIN social_media_dim.engagement e ON t.id_tweet = e.id_tweet
    """

    engine = context.resources.postgres_alchemy

    df = pd.read_sql(query, engine)

    log_dataframe_info(context, df, "Extracted data")

    return df

"""
Contains assets for uploading and downloading 'social media' data to and from MinIO.
"""

# Python
from typing import Any

# Dagster
from dagster import (
    AssetKey,
    AssetExecutionContext,
    Output,
    asset,
)

# Pipeline
from common.constants import get_metadata_categories
from common.resources import S3_Objects, BUCKET_NAME
from common.utils.datalake import (
    download_data_from_minio,
    upload_data_to_minio,
)
from social_media.assets.constants import (
    SocialMediaAssetCategories as Categories,
    Groups as SocialMediaGroups,
)


@asset(
    group_name=SocialMediaGroups.DATALAKE,
    required_resource_keys={"minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATA_ACQUISITION,
            Categories.STAGING,
            Categories.DATALAKE,
            Categories.TWEET_DATA,
        )
    },
)
def upload_social_media_data_to_minio(
    context: AssetExecutionContext, download_social_media_data: list
) -> Output:
    """Upload 'social media' data to MinIO."""

    data = download_social_media_data

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.SOCIAL_MEDIA_DATA.path

    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        asset_key="upload_social_media_data_to_minio",
        description="Social media data uploaded to MinIO",
    )


@asset(
    group_name=SocialMediaGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset({AssetKey(["upload_social_media_data_to_minio"])}),
    metadata={
        "categories": get_metadata_categories(
            Categories.SOCIAL_MEDIA,
            Categories.DATA_PROCESSING,
            Categories.DATALAKE,
            Categories.STAGING,
            Categories.TWEET_DATA,
        )
    },
)
def download_social_media_data_from_minio(
    context: AssetExecutionContext,
) -> Any:  # Union[list, dict]
    """Download 'social media' data from MinIO."""

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.SOCIAL_MEDIA_DATA.path

    json = download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_social_media_data_from_minio",
        description="Social media data downloaded from MinIO",
    )

    analyze_tweet_data(context, json)

    return json


def analyze_tweet_data(context: AssetExecutionContext, json: dict):
    """
    Make a basic analysis of the tweet data.
    """

    keys = collect_keys_from_json(json)

    # remove the [d/.+] for `keys`
    keys = "\n".join(sorted(remove_prefix_indexes(keys)))

    context.log.info(f"JSON keys structure:\n{keys}")

    tweets_number = len(json)
    context.log.info(f"Number of tweets:\n{tweets_number}")

    # Sample of first 3 tweets
    sample_tweets = "\n\n".join([str(tweet) for tweet in json[:3]])
    context.log.info(f"Sample of first 3 tweets:\n\n{sample_tweets}")


def remove_prefix_indexes(keys: set) -> set:
    """
    Remove the prefix indexes from the keys.
    """

    return {key.split("].")[1] for key in keys}


def collect_keys_from_json(json: dict, parent_key="", keys_set=None):
    """
    Traverse the keys of the JSON data.
    """

    if keys_set is None:
        keys_set = set()
    if isinstance(json, dict):
        for k, v in json.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            keys_set.add(full_key)
            collect_keys_from_json(v, full_key, keys_set)
    elif isinstance(json, list):
        for i, item in enumerate(json):
            full_key = f"{parent_key}[{i}]"
            collect_keys_from_json(item, full_key, keys_set)
    return keys_set

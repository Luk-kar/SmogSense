"""
Contains assets for uploading and downloading 'air quality sensor' data to and from MinIO.
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
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    MapPollutantGroups,
)
from common.resources import S3_Objects, BUCKET_NAME
from common.utils.datalake import (
    download_data_from_minio,
    upload_data_to_minio,
)
from air_quality.assets.pollution_map.assets.utils.preview_data import (
    preview_air_quality_map_pollutant_data,
)


@asset(
    group_name=MapPollutantGroups.DATALAKE,
    required_resource_keys={"minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_ACQUISITION,
            Categories.STAGING,
            Categories.DATALAKE,
            Categories.MAP_POLLUTANT_TABLE,
        )
    },
)
def upload_air_quality_map_pollutant_data_to_minio(
    context: AssetExecutionContext,
    download_air_quality_map_pollutant_data: dict,
) -> Output:
    """
    Upload all partitions of 'air quality map pollutant' data to MinIO.
    Aggregates data across all partitions and uploads as a single file.
    """

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.MAP_POLLUTANT_DATA.path

    # The input `download_air_quality_map_pollutant_data` will be a dictionary
    # where keys are partition keys, and values are the partition outputs.

    aggregated_data = download_air_quality_map_pollutant_data

    size = len(aggregated_data)

    if size == 0:
        context.log.error("❌ No data to upload to MinIO")
        raise Exception("No data to upload to MinIO")

    context.log.info(f"➡️ The size of the aggregated data is: {size} partitions")

    # Upload aggregated data to MinIO
    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=aggregated_data,
        asset_key="upload_air_quality_map_pollutant_data_to_minio",
        description="Aggregated air quality map pollutant data uploaded to MinIO",
    )


@asset(
    group_name=MapPollutantGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset(
        {AssetKey(["upload_air_quality_map_pollutant_data_to_minio"])}
    ),
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.DATALAKE,
            Categories.STAGING,
            Categories.SENSOR_DATA,
        )
    },
)
def download_air_quality_map_pollutant_data_from_minio(
    context: AssetExecutionContext,
) -> Any:  # Union[list, dict]
    """Download 'air quality map pollutant' data from MinIO."""
    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.MAP_POLLUTANT_DATA.path

    downloaded_data = download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_air_quality_map_pollutant_data_from_minio",
        description="Air quality map_pollutant data downloaded from MinIO",
    )

    preview_air_quality_map_pollutant_data(context, downloaded_data)

    return downloaded_data

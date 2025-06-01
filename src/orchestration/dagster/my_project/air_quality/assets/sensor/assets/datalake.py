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
    SensorGroups,
)
from common.resources import S3_Objects, BUCKET_NAME
from common.utils.datalake import (
    download_data_from_minio,
    upload_data_to_minio,
)


@asset(
    group_name=SensorGroups.DATALAKE,
    required_resource_keys={"minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_ACQUISITION,
            Categories.STAGING,
            Categories.DATALAKE,
            Categories.STATION_DATA,
        )
    },
)
def upload_air_quality_sensor_data_to_minio(
    context: AssetExecutionContext, download_air_quality_sensor_data: list
) -> Output:
    """Upload 'air quality sensor' data from the API to MinIO."""

    data = download_air_quality_sensor_data

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.SENSOR_DATA.path
    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        asset_key="upload_air_quality_sensor_data_to_minio",
        description="Air quality sensor data uploaded to MinIO",
    )


@asset(
    group_name=SensorGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset(
        {AssetKey(["upload_air_quality_sensor_data_to_minio"])}
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
def download_air_quality_sensor_data_from_minio(
    context: AssetExecutionContext,
) -> Any:  # Union[list, dict]
    """Download 'air quality sensor' data from MinIO."""
    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.SENSOR_DATA.path

    return download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_air_quality_sensor_data_from_minio",
        description="Air quality sensor data downloaded from MinIO",
    )

"""
Contains assets for uploading and downloading 'air quality station' data to and from MinIO.
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
    StationGroups,
)
from common.resources import S3_Objects, BUCKET_NAME
from common.utils.datalake import (
    download_data_from_minio,
    upload_data_to_minio,
)


@asset(
    group_name=StationGroups.DATALAKE,
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
def upload_air_quality_station_data_to_minio(
    context: AssetExecutionContext, download_air_quality_station_data: list
) -> Output:
    """Upload 'air quality station' data from the API to MinIO."""

    data = download_air_quality_station_data

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.STATION_DATA.path

    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        asset_key="upload_air_quality_station_data_to_minio",
        description="Air quality station data uploaded to MinIO",
    )


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset(
        {AssetKey(["upload_air_quality_station_data_to_minio"])}
    ),
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.DATALAKE,
            Categories.STAGING,
            Categories.STATION_DATA,
        )
    },
)
def download_air_quality_station_data_from_minio(
    context: AssetExecutionContext,
) -> Any:  # Union[list, dict]
    """Download 'air quality station' data from MinIO."""

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.STATION_DATA.path

    return download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_air_quality_station_data_from_minio",
        description="Air quality data station downloaded from MinIO",
    )

"""
Contains assets for uploading and downloading 'health death & illness' data to and from MinIO.
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

# Pipeline-like constants for Health
from health.constants import (
    HealthGroups,
    HealthAssetCategories as Categories,
)

# Common resources & utilities
from common.constants import get_metadata_categories
from common.resources import S3_Objects, BUCKET_NAME
from common.utils.datalake import (
    download_data_from_minio,
    upload_data_to_minio,
)


@asset(
    group_name=HealthGroups.DATALAKE,
    required_resource_keys={"minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATA_ACQUISITION,
            Categories.STAGING,
            Categories.DATALAKE,
        )
    },
)
def upload_health_death_illness_data_to_minio(
    context: AssetExecutionContext, download_health_death_illness_data: Any
) -> Output:
    """
    Upload 'health death & illness' data from the API to MinIO.
    """

    data = download_health_death_illness_data

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    # Define your own path or keep a separate S3_Objects for Health
    object_name = S3_Objects.HEALTH_DATA.path

    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        asset_key="upload_health_death_illness_data_to_minio",
        description="Health death & illness data uploaded to MinIO",
    )


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset(
        {AssetKey(["upload_health_death_illness_data_to_minio"])}
    ),
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATA_PROCESSING,
            Categories.DATALAKE,
            Categories.STAGING,
        )
    },
)
def download_health_death_illness_data_from_minio(
    context: AssetExecutionContext,
) -> Any:
    """
    Download 'health death & illness' data from MinIO.
    """

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.HEALTH_DATA.path

    return download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_health_death_illness_data_from_minio",
        description="Health death & illness data downloaded from MinIO",
    )


@asset(
    group_name=HealthGroups.DATALAKE,
    required_resource_keys={"minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DEMOGRAPHIC,
            Categories.DATA_ACQUISITION,
            Categories.STAGING,
            Categories.DATALAKE,
        )
    },
)
def upload_province_total_people_yearly_data_to_minio(
    context: AssetExecutionContext, download_province_total_people_yearly_data: Any
) -> Output:
    """
    Upload the total number of people in the province yearly to MinIO.
    """

    data = download_province_total_people_yearly_data

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.PROVINCE_TOTAL_PEOPLE_YEARLY.path

    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        asset_key="upload_province_total_people_yearly_data_to_minio",
        description="Province total people yearly data uploaded to MinIO",
    )


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset(
        {AssetKey(["upload_province_total_people_yearly_data_to_minio"])}
    ),
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATA_PROCESSING,
            Categories.DATALAKE,
            Categories.STAGING,
        )
    },
)
def download_province_total_people_yearly_data_from_minio(
    context: AssetExecutionContext,
) -> Any:
    """
    Download the total number of people in the province yearly from MinIO.
    """

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.PROVINCE_TOTAL_PEOPLE_YEARLY.path

    return download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_province_total_people_yearly_data_from_minio",
        description="Province total people yearly data downloaded from MinIO",
    )


@asset(
    group_name=HealthGroups.DATALAKE,
    required_resource_keys={"minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DEMOGRAPHIC,
            Categories.DATA_ACQUISITION,
            Categories.STAGING,
            Categories.DATALAKE,
        )
    },
)
def upload_country_total_people_yearly_data_to_minio(
    context: AssetExecutionContext, download_country_total_people_yearly_data: Any
) -> Output:
    """
    Upload the total number of people in the country yearly to MinIO.
    """

    data = download_country_total_people_yearly_data

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.COUNTRY_TOTAL_PEOPLE_YEARLY.path

    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        asset_key="upload_country_total_people_yearly_data_to_minio",
        description="Country total people yearly data uploaded to MinIO",
    )


@asset(
    group_name=HealthGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset(
        {AssetKey(["upload_country_total_people_yearly_data_to_minio"])}
    ),
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATA_PROCESSING,
            Categories.DATALAKE,
            Categories.STAGING,
        )
    },
)
def download_country_total_people_yearly_data_from_minio(
    context: AssetExecutionContext,
) -> Any:
    """
    Download the total number of people in the country yearly from MinIO.
    """

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.COUNTRY_TOTAL_PEOPLE_YEARLY.path

    return download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_country_total_people_yearly_data_from_minio",
        description="Country total people yearly data downloaded from MinIO",
    )

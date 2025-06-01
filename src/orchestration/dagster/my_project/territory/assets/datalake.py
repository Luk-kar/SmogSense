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
from territory.assets.constants import (
    TerritoryAssetCategories as Categories,
    TerritoryGroups,
)


@asset(
    group_name=TerritoryGroups.DATALAKE,
    required_resource_keys={"minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.TERRITORY,
            Categories.DATA_ACQUISITION,
            Categories.STAGING,
            Categories.DATALAKE,
        )
    },
)
def upload_province_territory_data_to_minio(
    context: AssetExecutionContext, download_provinces_data: dict
) -> Output:
    """Upload 'province territory' data to MinIO."""

    data = download_provinces_data

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.PROVINCE_TERRITORY_DATA.path

    return upload_data_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        asset_key="upload_province_territory_data_to_minio",
        description="Province territory data uploaded to MinIO",
    )


@asset(
    group_name=TerritoryGroups.DATA_PROCESSING,
    required_resource_keys={"minio_client"},
    non_argument_deps=frozenset(
        {AssetKey(["upload_province_territory_data_to_minio"])}
    ),
    metadata={
        "categories": get_metadata_categories(
            Categories.TERRITORY,
            Categories.DATA_PROCESSING,
            Categories.DATALAKE,
            Categories.STAGING,
        )
    },
)
def download_province_territory_data_from_minio(
    context: AssetExecutionContext,
) -> Any:  # Union[list, dict]
    """Download 'province_territory' data from MinIO."""

    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    object_name = S3_Objects.PROVINCE_TERRITORY_DATA.path

    json = download_data_from_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=bucket_name,
        object_name=object_name,
        asset_key="download_province_territory_data_from_minio",
        description="Province territory data downloaded from MinIO",
    )

    analyze_province_data(context, json)

    return json


def analyze_province_data(context: AssetExecutionContext, json: dict):
    """
    Perform basic analysis of the province data.
    """

    if "features" not in json:
        context.log.error("Invalid JSON format: missing 'features' key.")
        return

    features = json["features"]

    # Extract keys structure
    keys = collect_keys_from_json(json)
    context.log.info(f"JSON keys structure:\n{keys}")

    # Count provinces
    province_count = len(features)
    context.log.info(f"Number of provinces: {province_count}")

    # Extract names of provinces
    province_names = [
        feature["properties"].get("name", "Unknown") for feature in features
    ]
    context.log.info(f"Provinces found: {', '.join(province_names)}")

    # Sample data (first 3 provinces)
    sample_provinces = "\n\n".join(
        [
            f"ID: {feature['properties'].get('ID_1', 'N/A')}, "
            f"Name: {feature['properties'].get('name', 'N/A')}, "
            f"ISO: {feature['properties'].get('ISO', 'N/A')}, "
            f"Type: {feature['properties'].get('ENGTYPE_1', 'N/A')}"
            for feature in features[:3]
        ]
    )
    context.log.info(f"Sample of first 3 provinces:\n\n{sample_provinces}")

    # Geographical analysis: Count coordinate sets per province
    coordinate_counts = [
        len(feature["geometry"]["coordinates"][0]) if "geometry" in feature else 0
        for feature in features
    ]
    avg_coordinates = (
        sum(coordinate_counts) / len(coordinate_counts) if coordinate_counts else 0
    )
    context.log.info(
        f"Average number of coordinates per province: {avg_coordinates:.2f}"
    )

    # Example of coordinate sets for the first province
    first_province_coordinates = features[0]["geometry"]["coordinates"]
    context.log.info(
        f"Coordinates for the first province: {first_province_coordinates}"
    )


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

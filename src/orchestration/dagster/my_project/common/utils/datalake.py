"""Utility functions for working with MinIO."""

# Python
import sys
import json
from typing import Any

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    Failure,
    MetadataValue,
    Output,
)


def convert_list_to_json(data_list: list) -> bytes:
    """Convert a list to JSON bytes."""

    return json.dumps(data_list).encode("utf-8")


def upload_data_to_minio(
    context: AssetExecutionContext,
    s3_client,
    bucket_name: str,
    object_name: str,
    data: list,
    asset_key: str,
    description: str,
) -> Output:
    """Helper function for uploading data to MinIO."""
    # Convert list to JSON bytes
    data_to_upload = convert_list_to_json(data)
    context.log.info("Converted list to JSON bytes")

    ensure_bucket_exists(context, s3_client, bucket_name)
    upload_data_to_minio(context, s3_client, bucket_name, object_name, data_to_upload)

    # Log the AssetMaterialization with the MinIO object path
    context.log_event(
        AssetMaterialization(
            asset_key=asset_key,
            description=description,
            metadata={
                "MinIO Object": MetadataValue.path(f"s3://{bucket_name}/{object_name}")
            },
        )
    )

    return Output(None)


def upload_data_to_minio(context, s3_client, bucket_name, object_name, data_to_upload):
    """Upload a list of data as a JSON object to a specified MinIO bucket and log the materialization."""

    try:
        response = s3_client.put_object(
            Bucket=bucket_name, Key=object_name, Body=data_to_upload
        )
        context.log.info(f"Data uploaded to MinIO with response: {response}")
    except Exception as e:
        context.log.error(f"Error uploading data to MinIO: {e}")
        raise Failure(f"Failed to upload data to MinIO: {e}") from e


def ensure_bucket_exists(context, s3_client, bucket_name):
    """Ensure that the specified MinIO bucket exists, creating it if necessary."""

    existing_buckets = []

    try:

        existing_buckets = [
            b["Name"] for b in s3_client.list_buckets().get("Buckets", [])
        ]

        if bucket_name not in existing_buckets:
            s3_client.create_bucket(Bucket=bucket_name)
            context.log.info(f"Created bucket '{bucket_name}' in MinIO.")

    except Exception as e:
        context.log.info(f"Existing buckets:\n{existing_buckets}")
        context.log.error(f"Error checking/creating bucket: {e}")
        raise Failure(f"Failed to ensure bucket '{bucket_name}' exists: {e}") from e


def download_data_from_minio(
    context: AssetExecutionContext,
    s3_client,
    bucket_name: str,
    object_name: str,
    asset_key: str,
    description: str,
) -> Any:
    """Helper function for downloading data from MinIO."""
    # Download the JSON file from MinIO
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        data_bytes = response["Body"].read()
        context.log.info(f"Data downloaded from MinIO bucket '{bucket_name}'.")
    except Exception as e:
        context.log.error(f"Error downloading data from MinIO: {e}")
        raise Failure(f"Failed to download data from MinIO: {e}") from e

    bytes_size = sys.getsizeof(data_bytes)
    if bytes_size == 0:
        raise Failure("No data downloaded from MinIO")
    else:
        sainted_bytes_size = round((bytes_size / 1024), 2)

    # Log AssetMaterialization
    context.log_event(
        AssetMaterialization(
            asset_key=asset_key,
            description=description,
            metadata={"Data size (KB)": MetadataValue.float(sainted_bytes_size)},
        )
    )

    # Return JSON object
    return json.loads(data_bytes)

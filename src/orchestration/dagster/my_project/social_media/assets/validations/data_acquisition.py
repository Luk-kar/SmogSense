"""
This module contains asset checks for the health data acquisition assets.
"""

# Third-party
import json

# Dagster
from dagster import (
    AssetKey,
    asset_check,
    AssetCheckResult,
)


@asset_check(
    asset=AssetKey("download_social_media_data_from_minio"),
)
def check_download_social_media_data_from_minio(
    download_social_media_data_from_minio: list,  # JSON
) -> AssetCheckResult:
    """Checks if data if data is more than 1KB"""

    data_bytes = json.dumps(download_social_media_data_from_minio).encode("utf-8")
    data_size = len(data_bytes)

    # Check if the size is greater than 1KB (1024 bytes)
    if data_size > 1024:
        return AssetCheckResult(
            passed=True,
            metadata={
                "data_size_bytes": data_size,
                "message": "Data size is sufficient (greater than 1KB).",
            },
        )
    else:
        return AssetCheckResult(
            passed=False,
            metadata={
                "data_size_bytes": data_size,
                "message": "Data size is insufficient (less than 1KB).",
            },
        )

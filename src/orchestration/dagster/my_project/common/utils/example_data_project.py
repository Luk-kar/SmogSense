"""
Fetches a ZIP from a URL,
preserves its directory structure
while uploading its contents to MinIO,
and returns a summary of the upload.
"""

# Python
from pathlib import Path
import os
import tempfile
from typing import Any
import zipfile

# Third-party
import requests
from dagster import AssetExecutionContext

# Project
from common.utils.datalake import ensure_bucket_exists, upload_data_to_minio


def upload_zip_to_minio(
    url: str, context: AssetExecutionContext, s3_client: Any, bucket_name: str
):
    """One-line solution for ZIP upload with directory preservation"""

    extracted_files_count = 0
    total_size_bytes = 0

    with requests.get(
        url, stream=True
    ) as response, tempfile.TemporaryDirectory() as tmp_dir:

        zip_path = download_file_from_url(
            context, url, response, tmp_dir, "archive.zip"
        )

        context.log.info(f"📦 UNPACKING ARCHIVE to {tmp_dir}")
        with zipfile.ZipFile(zip_path) as zip_ref:
            # Get common parent directory of all files in ZIP
            members = zip_ref.namelist()
            common_prefix = os.path.commonpath(members) if members else ""
            context.log.info(
                f"🔍 Found {len(members)} files in archive, common prefix: '{common_prefix}'"
            )

            zip_ref.extractall(tmp_dir)

        # Determine content root dynamically
        content_root = Path(tmp_dir) / common_prefix if common_prefix else Path(tmp_dir)

        ensure_bucket_exists(context, s3_client, bucket_name)
        context.log.info(f"🪣 Verified/Created bucket '{bucket_name}'")

        context.log.info(f"🚚 STARTING UPLOAD to {bucket_name}")
        # Upload all extracted files and folders
        for file_path in content_root.rglob("*"):

            if file_path.is_file() and file_path != zip_path:

                # Create object name relative to content root
                object_name = str(file_path.relative_to(content_root))

                # Preserve POSIX path format
                object_name = object_name.replace("\\", "/")

                file_data = file_path.read_bytes()

                file_size = len(file_data)
                context.log.info(
                    f"📤 UPLOADING {object_name} "
                    f"({file_size/1024:.2f} KB) "
                    f"to {bucket_name}/{object_name}"
                )

                upload_data_to_minio(
                    context, s3_client, bucket_name, object_name, file_data
                )

                total_size_bytes += file_size
                extracted_files_count += 1

        total_size_mb = total_size_bytes / (1024 * 1024)
        context.log.info(
            f"🎉 UPLOAD COMPLETE - {extracted_files_count} files "
            f"({total_size_mb:.2f} MB) uploaded to {bucket_name}"
        )
        context.log.info(f"📁 Object prefix: {common_prefix or 'root directory'}")

        return {  # Add return statement
            "extracted_files": extracted_files_count,
            "object_prefix": common_prefix,
            "total_size_mb": total_size_mb,
        }


def download_file_from_url(
    context: AssetExecutionContext,
    url: str,
    response: requests.Response,
    tmp_dir: str,
    tmp_file_name: str,
):
    """
    Downloads a file from a URL to a directory and returns the download location.
    """

    context.log.info(
        f"🚀 INITIATING DOWNLOAD from {url} to temporary directory {tmp_dir}"
    )

    response.raise_for_status()
    context.log.info(f"✅ DOWNLOAD SUCCESS - Status code: {response.status_code}")

    file_path = Path(tmp_dir) / tmp_file_name
    file_path.write_bytes(response.content)
    context.log.info(
        f"📥 Saved the file to {file_path} ({file_path.stat().st_size/1024:.2f} KB)"
    )

    return file_path

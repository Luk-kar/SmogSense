"""
Uploading example project data to MinIO storage and
restoring a PostgreSQL database from a GitHub-hosted backup.
"""

# Python
import os
import tempfile

# Dagster
from dagster import AssetExecutionContext, asset, MetadataValue, AssetMaterialization

# Common
from common.constants import get_metadata_categories
from common.utils.example_data_project import (
    upload_zip_to_minio,
    download_file_from_url,
)
from common.resources import BUCKET_NAME

from common.utils.database.backup_management import (
    execute_pg_restore,
    extract_postgres_credentials,
    backup_file_validation,
    cleaning_database_for_restore,
)

# Third-party
import requests

# Warehouse
from warehouse.assets.constants import WarehouseCategories as Categories, Groups


@asset(
    group_name=Groups.EXAMPLE_PROJECT_DATA,
    required_resource_keys={"minio_client", "github_minio_data"},
    metadata={
        "categories": get_metadata_categories(
            Categories.MINIO,
            Categories.EXAMPLE_DATA,
        )
    },
)
def upload_example_project_data_to_minio(context: AssetExecutionContext):
    """
    Uploads structured example data from GitHub to MinIO storage bucket.

    Uses configured GitHub URL resource to locate the data package and MinIO client
    resource for storage operations. Preserves directory structure from ZIP archive.

    WARNING: It can overwrite the existing files!
    """
    # Get resources from context
    s3_client = context.resources.minio_client
    bucket_name = BUCKET_NAME
    github_minio_data = context.resources.github_minio_data

    # Execute upload
    result = upload_zip_to_minio(github_minio_data, context, s3_client, bucket_name)

    metadata = {
        "uploaded_files": MetadataValue.int(result["extracted_files"]),
        "total_size_mb": MetadataValue.float(result["total_size_mb"]),
        "minio_location": MetadataValue.url(
            f"{os.getenv('MINIO_ENDPOINT_URL')}/buckets/{BUCKET_NAME}/browse"
        ),
        "object_prefix": MetadataValue.text(result["object_prefix"]),
        "zip_source": MetadataValue.url(github_minio_data),
    }

    context.log_event(
        AssetMaterialization(
            asset_key="upload_example_project_data_asset",
            metadata=metadata,
        )
    )

    return metadata


@asset(
    group_name=Groups.EXAMPLE_PROJECT_DATA,
    required_resource_keys={"github_postgres_data", "postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DATABASE,
            Categories.DATABASE_RESTORE,
            Categories.EXAMPLE_DATA,
        )
    },
)
def restore_example_project_database(context: AssetExecutionContext):
    """
    Restores the database from a backup file specified by the
    'github_postgres_data' resource (a URL).

    Uses psycopg client and the configured GitHub Postgres as a data URL resource.

    WARNING: It can overwrite the existing tables and schemas!
    """

    database_backup_url = context.resources.github_postgres_data

    with requests.get(
        database_backup_url, stream=True
    ) as response, tempfile.TemporaryDirectory() as tmp_dir:

        database_backup_file_path = download_file_from_url(
            context, database_backup_url, response, tmp_dir, "restore_postgres_db.dump"
        )

        backup_file_validation(context, database_backup_file_path)

        engine, db_name, pg_restore_url = extract_postgres_credentials(context)

        cleaning_database_for_restore(context, engine)

        execute_pg_restore(context, pg_restore_url, db_name, database_backup_file_path)

        context.log.info("✅ Database restore completed successfully")

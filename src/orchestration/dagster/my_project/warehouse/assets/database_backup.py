"""
Module contains assets to backup the database.
"""

# Dagster
from dagster import AssetExecutionContext, asset

# Common
from common.constants import get_metadata_categories
from common.utils.database.backup_management import (
    backup_database_and_upload_to_minio,
    restore_database_from_backup,
)
from common.resources import S3_Objects, BUCKET_NAME

# Warehouse
from warehouse.assets.constants import WarehouseCategories as Categories, Groups


@asset(
    group_name=Groups.DATABASE_BACKUP,
    required_resource_keys={"postgres_alchemy", "minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DATABASE,
            Categories.DATABASE_BACKUP,
        )
    },
)
def backup_warehouse_database(context: AssetExecutionContext):
    """
    Asset to backup the warehouse database and upload the backup file to MinIO.
    """
    s3_client = context.resources.minio_client

    backup_database_and_upload_to_minio(
        context=context,
        s3_client=s3_client,
        bucket_name=BUCKET_NAME,
        backup_folder=S3_Objects.WAREHOUSE_BACKUP.value,
    )


@asset(
    group_name=Groups.DATABASE_BACKUP,
    required_resource_keys={"postgres_alchemy", "minio_client"},
    metadata={
        "categories": get_metadata_categories(
            Categories.DATABASE,
            Categories.DATABASE_RESTORE,
        )
    },
)
def restore_to_latest_warehouse_database_backup(context: AssetExecutionContext):
    """
    Asset to restore the warehouse database from the latest backup
    (or from a specified backup file).

    WARNING: It can overwrite the existing tables and schemas!
    """
    s3_client = context.resources.minio_client

    restore_database_from_backup(
        context=context,
        s3_client=s3_client,
        bucket_name=BUCKET_NAME,
        backup_folder=S3_Objects.WAREHOUSE_BACKUP.value,
    )

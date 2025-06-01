"""
This module provides utilities for managing PostgreSQL database backups and restores
using Dagster for orchestration and MinIO for storage.
"""

# Python
import os
from dataclasses import dataclass
from datetime import datetime
import hashlib
from pathlib import Path
import subprocess
from typing import Any, Union

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    Failure,
    MetadataValue,
)

# Common
from common.resources import FileExtensions
from common.constants import DATE_FILE_FORMAT

# SQLAlchemy
from sqlalchemy.engine import Engine

# .database
from common.utils.database.schema_operations import (
    drop_public_tables,
    drop_user_schemas,
    create_public_schema_if_not_exists,
)


@dataclass
class BackupParams:
    """
    Holds information needed to run and upload a database backup.
    """

    db_name: str
    user: str
    password: str
    host: str
    port: int
    local_backup_path: str
    bucket_name: str
    object_name: str
    minio_url: str


# Core workflows
def backup_database_and_upload_to_minio(
    context: AssetExecutionContext,
    s3_client,
    bucket_name: str,
    backup_folder: str,
):
    """
    Create a compressed backup of the database using pg_dump,
    then upload the backup file to the specified MinIO bucket.
    Checksums are computed to verify the integrity of the backup.

    Steps:
      1) Run pg_dump to create a local backup file
      2) Ensure the target S3 bucket exists
      3) Upload the local backup file to MinIO
      4) Verify the integrity of the backup
      5) Log the event with metadata about the backup
    """
    engine = context.resources.postgres_alchemy
    url = engine.url

    db_name = url.database
    user = url.username
    password = url.password
    host = url.host
    port = url.port

    # 1)
    local_filename, local_backup_path = generate_backup_filename(db_name)

    # 2)
    object_name, minio_url = build_backup_object_name(backup_folder, local_filename)

    # 3)
    params = BackupParams(
        db_name=db_name,
        user=user,
        password=password,
        host=host,
        port=port,
        local_backup_path=local_backup_path,
        bucket_name=bucket_name,
        object_name=object_name,
        minio_url=minio_url,
    )

    execute_backup_workflow(context, s3_client, params)

    # 4)
    local_checksum, remote_checksum = verify_backup_integrity(
        context, s3_client, params
    )

    # 5)
    context.log_event(
        AssetMaterialization(
            asset_key="warehouse_database_backup",
            description=f"Database backup of '{db_name}'",
            metadata={
                "Local backup file": MetadataValue.path(local_backup_path),
                "Backup S3 URL": MetadataValue.path(
                    f"{minio_url}/{bucket_name}/{object_name}"
                ),
                "Local checksum": local_checksum,
                "Remote checksum": remote_checksum,
            },
        )
    )


def restore_database_from_backup(
    context: AssetExecutionContext,
    s3_client,
    bucket_name: str,
    backup_folder: str,
    backup_filepath: str = None,
):
    """
    Restore a PostgreSQL database from a backup file stored in MinIO.

    Performs a full database restore by:
    1. Locating the specified backup or selecting the latest available
    2. Downloading the backup file
    3. Cleaning existing database structures
    4. Executing pg_restore with the downloaded backup

    Raises:
        Failure: If any of these occur:
            - No backups found in specified location
            - Backup file validation fails
            - Database cleanup operations fail
            - pg_restore process fails
    """

    engine, db_name, pg_restore_url, minio_url, local_temp_dir = (
        retrieve_connection_parameters(context)
    )

    backup_filepath = get_backup_filepath(
        context, s3_client, bucket_name, backup_folder, backup_filepath, minio_url
    )

    local_file_path = download_backup_file(
        context, s3_client, bucket_name, backup_filepath, minio_url, local_temp_dir
    )

    backup_file_validation(context, local_file_path)

    cleaning_database_for_restore(context, engine)

    execute_pg_restore(context, pg_restore_url, db_name, local_file_path)


# Sub-operations
def execute_backup_workflow(
    context: AssetExecutionContext, s3_client, params: BackupParams
):
    """
    Execute the backup workflow.
    """
    run_pg_dump(context, params)
    ensure_bucket_exists(context, s3_client, params)
    upload_backup_to_minio(context, s3_client, params)


def build_backup_object_name(backup_folder: str, local_filename: str):
    """
    Build the object name for the backup file in MinIO.
    """
    object_name = f"{backup_folder}/{local_filename}"
    minio_url = get_minio_browser_url()

    return object_name, minio_url


def generate_backup_filename(db_name: str):
    """
    Generate a unique filename for the backup file.
    """

    directory = "/tmp"  # It's a a standard temporary directory for Unix-like systems.
    timestamp = datetime.now().strftime(DATE_FILE_FORMAT)
    local_filename = f"{db_name}_backup_{timestamp}.{FileExtensions.DUMP.value}"
    local_backup_path = os.path.join(directory, local_filename)

    return local_filename, local_backup_path


def run_pg_dump(context: AssetExecutionContext, params: BackupParams) -> None:
    """
    Run pg_dump to create local backup of the database in custom format.
    """
    command = [
        "pg_dump",
        (
            f"--dbname=postgresql://{params.user}:{params.password}@{params.host}:"
            f"{params.port}/{params.db_name}"
        ),
        "-Fc",  # custom format
        "-f",
        params.local_backup_path,
    ]

    try:
        context.log.info(
            f"➡️ Starting backup of '{params.db_name}' to '{params.local_backup_path}'..."
        )
        subprocess.run(command, check=True)
        context.log.info(
            f"✅ Successfully created local backup '{params.local_backup_path}'."
        )
    except subprocess.CalledProcessError as e:
        context.log.error(f"❌ Backup failed for '{params.db_name}': {e}")
        raise Failure(f"Backup failed for '{params.db_name}': {e}") from e


def get_backup_filepath(
    context: AssetExecutionContext,
    s3_client: Any,
    bucket_name: str,
    backup_folder: str,
    backup_filepath: str,
    minio_url: str,
):
    """
    Get the backup file path from the latest backup in the folder.
    """

    if not backup_filepath:
        backup_filepath = fetch_latest_backup_filepath(
            context, s3_client, bucket_name, backup_folder, minio_url
        )
    else:
        context.log.info(f"➡️ Using specified backup file: '{backup_filepath}'")
    return backup_filepath


def fetch_latest_backup_filepath(
    context: AssetExecutionContext,
    s3_client: Any,
    bucket_name: str,
    backup_folder: str,
    minio_url: str,
):
    """
    Find the latest backup file in the specified folder.

    Raises:
        Failure: If no backup files are found in the folder.
    """

    context.log.info(f"➡️ Searching for latest backup in folder '{backup_folder}'...")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=backup_folder)

        objects = response.get("Contents", [])
        if not objects:
            raise Failure(
                f"No backup files found in '{minio_url}/{bucket_name}/{backup_folder}'."
            )

            # Sort by LastModified descending
        objects_sorted = sorted(
            objects, key=lambda obj: obj["LastModified"], reverse=True
        )

        latest_obj = objects_sorted[0]
        backup_filepath = latest_obj[
            "Key"
        ]  # e.g. "warehouse_backup/smogsense_backup_2025-01-28_09-53-45.dump"

        context.log.info(f"➡️ Latest backup file is '{backup_filepath}'.")

    except Exception as e:
        raise Failure(f"Failed to find latest backup in '{backup_folder}': {e}") from e

    return backup_filepath


def execute_pg_restore(
    context: AssetExecutionContext,
    pg_restore_url: str,
    db_name: str,
    local_file_path: str,
):
    """
    Restore a PostgreSQL database from a backup file using the pg_restore command.

    Raises:
        Failure: If the pg_restore command fails.
    """
    # -Fc indicates a custom format dump
    # -d is the target database
    # --clean + --if-exists drops objects first to avoid duplication
    command = [
        "pg_restore",
        "-Fc",
        "--clean",
        "--if-exists",
        "-d",
        pg_restore_url,
        str(local_file_path),
    ]

    try:
        context.log.info(
            f"➡️ Restoring database '{db_name}' from '{local_file_path}'..."
        )
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,  # Decode output to strings
        )
        context.log.info(f"✅ Database '{db_name}' restored successfully.")

    except subprocess.CalledProcessError as e:
        error_msg = (
            f"❌ Restore failed for '{db_name}' (exit {e.returncode}):\n"
            f"Command: {' '.join(str(arg) for arg in e.cmd)}\n"
            f"Stderr: {e.stderr}\n"
            f"Stdout: {e.stdout}"
        )

        context.log.error(error_msg)
        raise Failure(error_msg) from e

    finally:
        # Remove local file to free up space
        if os.path.exists(local_file_path):
            os.remove(local_file_path)


def verify_backup_integrity(
    context: AssetExecutionContext, s3_client, params: BackupParams
):
    """
    Verify integrity by comparing the SHA-256 checksums of local and remote copies.
    Removes the local file afterward.
    """
    # NOTE: For bigger databases, you can use:
    # https://www.postgresql.org/docs/current/app-pgchecksums.html

    context.log.info("➡️ Verifying backup integrity...")

    # a) Compute local file checksum
    local_checksum = compute_sha256_checksum(params.local_backup_path)

    # b) Download the remote object to a temp file
    remote_temp_path = params.local_backup_path + ".download"

    try:

        s3_client.download_file(
            params.bucket_name, params.object_name, remote_temp_path
        )
        remote_checksum = compute_sha256_checksum(remote_temp_path)

    except Exception as e:

        context.log.error(f"❌ Error verifying backup from MinIO: {e}")
        raise Failure(f"Failed to download or hash backup from MinIO: {e}") from e

    finally:

        if os.path.exists(remote_temp_path):
            os.remove(remote_temp_path)
        if os.path.exists(params.local_backup_path):
            os.remove(params.local_backup_path)

    if local_checksum != remote_checksum:

        context.log.error(
            f"❌ Checksum mismatch! local='{local_checksum}' vs remote='{remote_checksum}'"
        )
        raise Failure("Backup verification failed: checksums do not match.")

    else:
        context.log.info("✅ Backup verification succeeded. Checksums match.")

    return local_checksum, remote_checksum


def compute_sha256_checksum(file_path: str) -> str:
    """
    Compute the SHA-256 checksum of a local file.
    Checksum is used to verify the identity of the file.
    """
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:

        # Read file in chunks to avoid memory issues with large files
        # The DB can be huge, so it's better to read in chunks
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def ensure_bucket_exists(
    context: AssetExecutionContext, s3_client, params: BackupParams
) -> None:
    """
    Ensure the target S3 bucket exists.
    """
    try:
        existing_buckets = [
            b["Name"] for b in s3_client.list_buckets().get("Buckets", [])
        ]

        if params.bucket_name not in existing_buckets:

            s3_client.create_bucket(Bucket=params.bucket_name)
            context.log.info(f"➡️ Created bucket '{params.bucket_name}' in MinIO.")

    except Exception as e:

        context.log.error(
            f"❌ Error checking/creating bucket '{params.bucket_name}': {e}"
        )
        raise Failure(
            f"Failed to ensure bucket '{params.bucket_name}' exists: {e}"
        ) from e


def upload_backup_to_minio(
    context: AssetExecutionContext, s3_client, params: BackupParams
) -> None:
    """
    Upload the local backup file to MinIO.
    """
    try:
        s3_client.upload_file(
            params.local_backup_path, params.bucket_name, params.object_name
        )
        context.log.info(
            f"✅ Backup uploaded to '{params.minio_url}/{params.bucket_name}/{params.object_name}'."
        )
    except Exception as e:

        context.log.error(f"❌ Error uploading backup to MinIO: {e}")
        raise Failure(f"Failed to upload backup to MinIO: {e}") from e


def get_minio_browser_url():
    """
    Get the MinIO browser URL from the environment or use the default.
    """

    minio_web_port = os.getenv("MINIO_HOST_PORT_WEB", "9001")
    minio_url = f"http://localhost:{minio_web_port}/browser"
    return minio_url


def retrieve_connection_parameters(context: AssetExecutionContext):
    """
    Get connection info for the database from the context.
    """

    engine, db_name, pg_restore_url = extract_postgres_credentials(context)

    minio_url = get_minio_browser_url()

    local_temp_dir = "/tmp"
    return engine, db_name, pg_restore_url, minio_url, local_temp_dir


def extract_postgres_credentials(
    context: AssetExecutionContext,
) -> tuple[Any, str, str]:
    """
    Returns:
    - SQLAlchemy engine instance
    - Database name
    - pg_restore connection string (postgresql://user:pass@host:port/db)
    """
    engine = context.resources.postgres_alchemy
    db_url = engine.url

    user = db_url.username
    password = db_url.password
    host = db_url.host
    port = db_url.port
    db_name = db_url.database

    pg_restore_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    return engine, db_name, pg_restore_url


def download_backup_file(
    context: AssetExecutionContext,
    s3_client: Any,
    bucket_name: str,
    backup_filepath: str,
    minio_url: str,
    local_temp_dir: str,
):
    """
    Download the backup file from MinIO to a local temp directory.
    """

    local_filename = os.path.basename(backup_filepath)
    local_file_path = os.path.join(local_temp_dir, local_filename)

    try:
        context.log.info(
            f"➡️ Downloading '{minio_url}/{bucket_name}/{backup_filepath}'"
            f"to '{local_file_path}'..."
        )

        s3_client.download_file(bucket_name, backup_filepath, local_file_path)
        context.log.info(f"✅ Successfully downloaded backup to '{local_file_path}'.")

    except Exception as e:
        context.log.error(f"❌ Error downloading backup: {e}")
        raise Failure(f"Failed to download backup '{backup_filepath}': {e}") from e
    return local_file_path


def backup_file_validation(
    context: AssetExecutionContext, database_backup_file_path: Union[Path, str]
):
    """
    Validates a PostgreSQL database backup file for restoration suitability.

    Performs the following checks:
    1. File is not empty (size > 0 bytes)
    2. File header matches PostgreSQL backup formats:
       - Custom format (magic bytes 'PGDMP')
       - Plain SQL dump (contains header comment)

    Raises:
        ValueError: If any validation check fails
        OSError: If file access operations fail
        UnicodeDecodeError: If plain text header contains invalid
    """
    context.log.info(f"🔍 Validating backup file: {database_backup_file_path}")

    if isinstance(database_backup_file_path, str):
        database_backup_file_path = Path(database_backup_file_path)

    if not database_backup_file_path.exists():
        raise FileNotFoundError(
            f"❌ Backup file not found: {database_backup_file_path}"
        )

    # Check file size validation
    file_size = database_backup_file_path.stat().st_size
    if file_size == 0:
        raise ValueError("❌ Downloaded database backup file is empty (0 bytes)")

    context.log.info(f"📦 Backup file size: {file_size/1024:.2f} KB")

    # Verify PostgreSQL backup format magic header
    with open(database_backup_file_path, "rb") as f:

        header = f.read(5)

        if header != b"PGDMP":

            # Check for plain SQL dump as fallback
            f.seek(0)
            first_line = f.readline().decode("utf-8", errors="ignore")

            if "-- PostgreSQL database dump" not in first_line:
                raise ValueError(
                    f"❌ Invalid backup format. Expected:\n"
                    f"- PostgreSQL custom format (PGDMP header) or\n"
                    f"- Plain SQL dump (header comment)\n"
                    f"Found header: {header!r}"
                )

            context.log.warning(
                "⚠️ Plain SQL dump detected - ensure psql is used for restoration"
            )

    context.log.info("✅ Backup file validation passed - valid PostgreSQL format")


def cleaning_database_for_restore(context: AssetExecutionContext, engine: Engine):
    """
    Prepares the database for restoration by removing existing schemas and tables.
    """

    context.log.info("🧹 Starting database cleanup before restore")

    create_public_schema_if_not_exists(context, engine)
    drop_user_schemas(context, engine)
    drop_public_tables(context, engine)

    context.log.info("✅ Database cleanup completed")

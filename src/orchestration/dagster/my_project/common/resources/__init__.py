"""
Provides functions and classes to load, clean, and transform datasets.

Includes utilities for handling missing data, normalization, and feature extraction.

Usage:
    from data_processing import DataCleaner, normalize_data
"""

# Python
from enum import Enum
from dataclasses import dataclass
import os

# Third-party
import boto3
import psycopg

# Dagster
from dagster import EnvVar, resource

# SQLAlchemy
from sqlalchemy import create_engine

# ==============================================================================
# minio service
# ==============================================================================


# https://stackoverflow.com/questions/67285745/how-can-i-get-minio-access-and-secret-key
@resource(
    config_schema={
        "endpoint_url": str,
        "aws_access_key_id": str,
        "aws_secret_access_key": str,
    }
)
def minio_client(context):
    """
    A Dagster resource that creates a MinIO client
    for interacting with an S3-compatible storage service.
    """
    config = context.resource_config
    return boto3.client(
        "s3",
        endpoint_url=config["endpoint_url"],
        aws_access_key_id=config["aws_access_key_id"],
        aws_secret_access_key=config["aws_secret_access_key"],
    )


BUCKET_NAME = "my-datalake"  # change this to your bucket name


class BucketPipelineStages(Enum):
    """
    Stages of the data pipeline.
    """

    DATA_ACQUISITION = "data_acquisition"
    WAREHOUSE_BACKUP = "warehouse_backup"


class BucketDataSources(Enum):
    """
    Data categories sources for the data pipeline.
    """

    AIR_QUALITY = "air_quality"
    HEALTH = "health"
    DEMOGRAPHIC = "demographic"
    SOCIAL_MEDIA = "social_media"
    TERRITORY = "territory"


class BucketDataAPI(Enum):
    """
    APIs used for the data pipeline.
    """

    STATION = "station"
    ANNUAL_STATISTICS = "annual_statistics"
    SENSOR = "sensor"
    MAP_POLLUTANT = "map_pollutant"
    DEATH_ILLNESS = "death_illness"
    SOCIAL_MEDIA = "social_media"
    TOTAL_PEOPLE_COUNTRY = "country"
    TOTAL_PEOPLE_PROVINCE = "province"
    PROVINCE_TERRITORY = "province_territory"


class FileExtensions(Enum):
    """
    Types of files used in the data pipeline.
    """

    JSON = "json"
    CSV = "csv"
    DUMP = "dump"  # for PostgreSQL dumps


@dataclass(frozen=True)
class S3RawDataFile:
    """
    Represents an object path in an S3 bucket.

    This dataclass encapsulates the details required to construct the path
    to a specific object stored in an S3 bucket. The path is constructed
    based on the stage of the data pipeline, the source of the data, the
    specific API used to fetch the data, and the file extension of the data.
    """

    stage: BucketPipelineStages
    source: BucketDataSources
    api: BucketDataAPI
    extension: FileExtensions

    @property
    def path(self) -> str:
        """
        Constructs the S3 bucket path.
        An example:
        ```
        data_acquisition/air_quality/station.json
        ```
        """
        return f"{self.stage.value}/{self.source.value}/{self.api.value}.{self.extension.value}"


class S3_Objects:
    """
    A collection of S3 bucket entries for the data pipeline.
    """

    STATION_DATA = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.AIR_QUALITY,
        api=BucketDataAPI.STATION,
        extension=FileExtensions.JSON,
    )
    ANNUAL_STATISTICS_DATA = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.AIR_QUALITY,
        api=BucketDataAPI.ANNUAL_STATISTICS,
        extension=FileExtensions.JSON,
    )
    SENSOR_DATA = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.AIR_QUALITY,
        api=BucketDataAPI.SENSOR,
        extension=FileExtensions.JSON,
    )
    MAP_POLLUTANT_DATA = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.AIR_QUALITY,
        api=BucketDataAPI.MAP_POLLUTANT,
        extension=FileExtensions.JSON,
    )
    HEALTH_DATA = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.HEALTH,
        api=BucketDataAPI.DEATH_ILLNESS,
        extension=FileExtensions.JSON,
    )
    PROVINCE_TOTAL_PEOPLE_YEARLY = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.DEMOGRAPHIC,
        api=BucketDataAPI.TOTAL_PEOPLE_PROVINCE,
        extension=FileExtensions.JSON,
    )
    COUNTRY_TOTAL_PEOPLE_YEARLY = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.DEMOGRAPHIC,
        api=BucketDataAPI.TOTAL_PEOPLE_COUNTRY,
        extension=FileExtensions.JSON,
    )
    SOCIAL_MEDIA_DATA = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.SOCIAL_MEDIA,
        api=BucketDataAPI.SOCIAL_MEDIA,
        extension=FileExtensions.JSON,
    )
    PROVINCE_TERRITORY_DATA = S3RawDataFile(
        stage=BucketPipelineStages.DATA_ACQUISITION,
        source=BucketDataSources.TERRITORY,
        api=BucketDataAPI.PROVINCE_TERRITORY,
        extension=FileExtensions.JSON,
    )
    WAREHOUSE_BACKUP = BucketPipelineStages.WAREHOUSE_BACKUP


# Configure the MinIO client resource using environment variables
configured_minio_client = minio_client.configured(
    {
        "endpoint_url": EnvVar("MINIO_ENDPOINT_URL").get_value(),
        "aws_access_key_id": EnvVar("MINIO_ACCESS_KEY_ID").get_value(),
        "aws_secret_access_key": EnvVar(
            "MINIO_SECRET_ACCESS_KEY",
        ).get_value(),
    }
)

# ==============================================================================
# postgres service
# ==============================================================================

POSTGRES_CONFIG_SCHEMA = {
    "host": EnvVar("POSTGRES_HOST").get_value(),
    "port": int(EnvVar("POSTGRES_HOST_PORT").get_value()),
    "user": EnvVar("POSTGRES_USER").get_value(),
    "password": EnvVar("POSTGRES_PASSWORD").get_value(),
    "dbname": EnvVar("POSTGRES_WAREHOUSE_DB").get_value(),
}


@resource(
    config_schema={
        "host": str,
        "port": int,
        "user": str,
        "password": str,
        "dbname": str,
    }
)
def postgres_resource_psycopg(context):
    """
    A Dagster resource that creates a connection to a PostgreSQL database using the psycopg library.
    """
    config = context.resource_config
    conn = psycopg.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        dbname=config["dbname"],
    )
    return conn


# Configure the PostgreSQL resource
configured_postgres_resource_psycopg = postgres_resource_psycopg.configured(
    POSTGRES_CONFIG_SCHEMA
)


@resource(
    config_schema={
        "host": str,
        "port": int,
        "user": str,
        "password": str,
        "dbname": str,
    }
)
def postgres_resource_alchemy(context):
    """
    A Dagster resource that creates a SQLAlchemy engine for connecting to a PostgreSQL database.
    """

    # Construct the SQLAlchemy connection string
    config = context.resource_config
    connection_string = (
        f"postgresql+psycopg2://"
        f"{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
    )

    # Create and return the SQLAlchemy engine
    engine = create_engine(connection_string)
    return engine


# Configure the alchemy_postgres_resource with environment variables
configured_postgres_resource_alchemy = postgres_resource_alchemy.configured(
    POSTGRES_CONFIG_SCHEMA
)

# ==============================================================================
# example data for project url sources
# ==============================================================================

EXAMPLE_DATA_REPOSITORY_URL = "https://github.com/Luk-kar/smogsense-data"


@resource(
    config_schema={
        "github_repo": str,
        "service_path": str,
        "file_name": str,
    }
)
def github_raw_url_resource(context) -> str:
    """Resource that constructs raw GitHub URL from parameters"""
    base_url = context.resource_config["github_repo"].replace(
        "github.com", "raw.githubusercontent.com"
    )
    return f"{base_url}/main/{context.resource_config['service_path']}/{context.resource_config['file_name']}"


# Configured project data examples

GITHUB_DATA_REPO = EnvVar("GITHUB_DATA_REPO").get_value()

configured_github_minio_data_url_resource = github_raw_url_resource.configured(
    {
        "github_repo": GITHUB_DATA_REPO,
        "service_path": EnvVar("GITHUB_MINIO_SERVICE_PATH").get_value(),
        "file_name": EnvVar("GITHUB_MINIO_FILE_NAME").get_value(),
    }
)

configured_github_postgres_data_url_resource = github_raw_url_resource.configured(
    {
        "github_repo": GITHUB_DATA_REPO,
        "service_path": EnvVar("GITHUB_POSTGRES_SERVICE_PATH").get_value(),
        "file_name": EnvVar("GITHUB_POSTGRES_FILE_NAME").get_value(),
    }
)

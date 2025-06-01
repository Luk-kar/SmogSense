"""
Defines common categories, groups, and utility functions to organize and manage metadata
for Dagster assets across multiple domains (e.g., air quality, health, social).
"""

# Dagster
from dagster import MetadataValue


def get_metadata_categories(*categories: str) -> MetadataValue:
    """
    Creates a metadata text value by joining the provided categories with commas.
    Used as a standard approach for assigning metadata to Dagster assets.
    """
    return MetadataValue.text(", ".join(categories))


class BaseAssetCategories:
    """
    Base class for defining categories used to classify assets across different domains.
    You can extend this class in domain-specific modules (e.g., air_quality, health).
    Use it as metadata to directly describe the asset's purpose and function.
    """

    # Common categories that both 'air_quality' and 'health' might share:
    DATA_ACQUISITION = "data_acquisition"
    DATALAKE = "datalake"
    STAGING = "staging"
    DATA_PROCESSING = "data_processing"
    DATABASE = "database"
    DATABASE_UPLOAD = "database_upload"
    DATABASE_INIT_TABLE = "database_init_table"
    DATABASE_NORMALIZED = "database_normalized"
    DATA_MODELING = "data_modeling"
    DATABASE_BACKUP = "database_backup"
    # Add more if there are other universal categories


class BaseGroups:
    """
    Defines general assets' groups for the data pipelines.
    """

    # Core pipeline grouping phases:
    DATA_ACQUISITION = "data_acquisition"
    DATALAKE = "datalake"
    DATA_PROCESSING = "data_processing"
    DATABASE = "database"
    DATABASE_UPLOAD = "database_upload"
    DATABASE_DROP_SCHEMA = "database_drop_schema"
    DATABASE_BACKUP = "database_backup"
    # Add more if there are other universal groups


# Avoid illegal characters in the filename
# https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
# https://stackoverflow.com/a/31976060/12490791
DATE_FILE_FORMAT = "%Y-%m-%d_%H+%M+%S"

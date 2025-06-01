"""
Contains asset checks for validating the consistency and structure 
of data between Pandas DataFrames and PostgreSQL database tables, 
leveraging Dagster and SQLAlchemy. 
It includes functions for comparing row counts, column schemas, 
and data types to ensure data integrity. 
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetIn,
    AssetCheckExecutionContext,
    AssetKey,
    asset_check,
)

# Pipeline
from air_quality.models.map_pollution_models import (
    Pollutant,
    Measurement,
    GeometryRecord,
)
# fmt: off
from air_quality.assets.\
    pollution_map.assets.database_upload import (
    upload_data_map_pollutants,
    upload_data_map_measurements,
    upload_data_map_geometry,
)
# fmt: on
from common.utils.database.data_validation import (
    compare_uploaded_database_data,
)


@asset_check(
    asset=upload_data_map_pollutants,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_map_pollutants": AssetIn(
            key=AssetKey("create_dataframe_map_pollutants")
        )
    },
)
def check_pollutant_data(
    context: AssetCheckExecutionContext,
    create_dataframe_map_pollutants: pd.DataFrame,
):
    """Checks if 'pollutant' data matches the data in the database."""

    return compare_uploaded_database_data(
        context,
        create_dataframe_map_pollutants,
        Pollutant,
    )


@asset_check(
    asset=upload_data_map_measurements,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_map_measurements": AssetIn(
            key=AssetKey("create_dataframe_map_measurements")
        )
    },
)
def check_measurement_data(
    context: AssetCheckExecutionContext,
    create_dataframe_map_measurements: pd.DataFrame,
):
    """Checks if 'measurement' data matches the data in the database."""

    return compare_uploaded_database_data(
        context,
        create_dataframe_map_measurements,
        Measurement,
    )


@asset_check(
    asset=upload_data_map_geometry,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_map_geometry": AssetIn(
            key=AssetKey("create_dataframe_map_geometry")
        )
    },
)
def check_geometry_data(
    context: AssetCheckExecutionContext,
    create_dataframe_map_geometry: pd.DataFrame,
):
    """Checks if 'geometry' data matches the data in the database."""

    return compare_uploaded_database_data(
        context,
        create_dataframe_map_geometry,
        GeometryRecord,
    )

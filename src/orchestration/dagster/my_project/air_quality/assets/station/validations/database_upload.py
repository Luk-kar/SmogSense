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
from air_quality.models.station_models import (
    Area,
    Location,
    Province,
    Station,
)
from air_quality.assets.station.assets.database_upload import (
    upload_data_province,
    upload_data_area,
    upload_data_location,
    upload_data_station,
)
from common.utils.database.data_validation import (
    compare_uploaded_database_data,
)


@asset_check(
    asset=upload_data_province,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_province": AssetIn(key=AssetKey("create_dataframe_province"))
    },
)
def check_province_data(
    context: AssetCheckExecutionContext,
    create_dataframe_province: pd.DataFrame,
):
    """Checks if 'province' data matches the data in the database."""

    # Download province table and match it with the dataframe

    return compare_uploaded_database_data(context, create_dataframe_province, Province)


@asset_check(
    asset=upload_data_area,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_area": AssetIn(key=AssetKey("create_dataframe_area"))
    },
)
def check_area_data(
    context: AssetCheckExecutionContext,
    create_dataframe_area: pd.DataFrame,
):
    """Asset check for 'area' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_area, Area)


@asset_check(
    asset=upload_data_location,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_location": AssetIn(key=AssetKey("create_dataframe_location"))
    },
)
def check_location_data(
    context: AssetCheckExecutionContext,
    create_dataframe_location: pd.DataFrame,
):
    """Asset check for 'location' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_location, Location)


@asset_check(
    asset=upload_data_station,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_station": AssetIn(key=AssetKey("create_dataframe_station"))
    },
)
def check_station_data(
    context: AssetCheckExecutionContext,
    create_dataframe_station: pd.DataFrame,
):
    """Asset check for 'station' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_station, Station)

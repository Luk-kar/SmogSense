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
from air_quality.models.annual_statistics_models import (
    Province,
    ZoneType,
    Zone,
    Station,
    Indicator,
    TimeAveraging,
    Measurement,
)
# fmt: off
from air_quality.assets.\
    annual_statistics.assets.database_upload import (
    upload_data_province_annual_statistics,
    upload_data_zone_type,
    upload_data_zone,
    upload_data_station_annual_statistics,
    upload_data_indicator,
    upload_data_time_averaging,
    upload_data_measurement,
)
# fmt: on
from common.utils.database.data_validation import (
    compare_uploaded_database_data,
)


@asset_check(
    asset=upload_data_province_annual_statistics,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_province": AssetIn(
            key=AssetKey("create_dataframe_province_annual_statistics")
        )
    },
)
def check_province_data(
    context: AssetCheckExecutionContext,
    create_dataframe_province: pd.DataFrame,
):
    """Checks if 'province' data matches the data in the database."""

    return compare_uploaded_database_data(context, create_dataframe_province, Province)


@asset_check(
    asset=upload_data_zone_type,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_zone_type": AssetIn(
            key=AssetKey("create_dataframe_zone_type")
        )
    },
)
def check_zone_type_data(
    context: AssetCheckExecutionContext,
    create_dataframe_zone_type: pd.DataFrame,
):
    """Asset check for 'zone_type' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_zone_type, ZoneType)


@asset_check(
    asset=upload_data_zone,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_zone": AssetIn(key=AssetKey("create_dataframe_zone"))
    },
)
def check_zone_data(
    context: AssetCheckExecutionContext,
    create_dataframe_zone: pd.DataFrame,
):
    """Asset check for 'zone' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_zone, Zone)


@asset_check(
    asset=upload_data_station_annual_statistics,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_station": AssetIn(
            key=AssetKey("create_dataframe_station_annual_statistics")
        )
    },
)
def check_station_data(
    context: AssetCheckExecutionContext,
    create_dataframe_station: pd.DataFrame,
):
    """Asset check for 'station' data uploaded to the database."""

    return compare_uploaded_database_data(context, create_dataframe_station, Station)


@asset_check(
    asset=upload_data_indicator,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_indicator": AssetIn(
            key=AssetKey("create_dataframe_indicator")
        )
    },
)
def check_indicator_data(
    context: AssetCheckExecutionContext,
    create_dataframe_indicator: pd.DataFrame,
):
    """Asset check for 'indicator' data uploaded to the database."""

    return compare_uploaded_database_data(
        context, create_dataframe_indicator, Indicator
    )


@asset_check(
    asset=upload_data_time_averaging,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_time_averaging": AssetIn(
            key=AssetKey("create_dataframe_time_averaging")
        )
    },
)
def check_time_averaging_data(
    context: AssetCheckExecutionContext,
    create_dataframe_time_averaging: pd.DataFrame,
):
    """Asset check for 'time_averaging' data uploaded to the database."""

    return compare_uploaded_database_data(
        context, create_dataframe_time_averaging, TimeAveraging
    )


@asset_check(
    asset=upload_data_measurement,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_measurement": AssetIn(
            key=AssetKey("create_dataframe_measurement")
        )
    },
)
def check_measurement_data(
    context: AssetCheckExecutionContext,
    create_dataframe_measurement: pd.DataFrame,
):
    """Asset check for 'measurement' data uploaded to the database."""

    return compare_uploaded_database_data(
        context, create_dataframe_measurement, Measurement
    )

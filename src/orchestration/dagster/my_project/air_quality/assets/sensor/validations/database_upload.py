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
from air_quality.models.sensor_models import (
    Indicator,
    Sensor,
)
from air_quality.assets.sensor.assets.database_upload import (
    upload_data_sensor_indicator,
    upload_data_sensor,
)
from common.utils.database.data_validation import (
    compare_uploaded_database_data,
)


@asset_check(
    asset=upload_data_sensor_indicator,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_sensor_indicator": AssetIn(
            key=AssetKey("create_dataframe_sensor_indicator")
        )
    },
)
def check_sensor_indicator_data(
    context: AssetCheckExecutionContext,
    create_dataframe_sensor_indicator: pd.DataFrame,
):
    """Check 'indicator' data in PostgreSQL database"""

    return compare_uploaded_database_data(
        context, create_dataframe_sensor_indicator, Indicator
    )


@asset_check(
    asset=upload_data_sensor,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "create_dataframe_sensor": AssetIn(key=AssetKey("create_dataframe_sensor"))
    },
)
def check_sensor_data(
    context: AssetCheckExecutionContext,
    create_dataframe_sensor: pd.DataFrame,
):
    """Check 'sensor' data in PostgreSQL database"""

    return compare_uploaded_database_data(context, create_dataframe_sensor, Sensor)

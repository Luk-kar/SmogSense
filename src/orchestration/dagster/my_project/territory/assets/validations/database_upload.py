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
from territory.models import Province
# fmt: off
from territory.assets.database_upload import (
    upload_data_province_territory
)
# fmt: on
from common.utils.database.data_validation import (
    compare_uploaded_database_data,
)


@asset_check(
    asset=upload_data_province_territory,
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "extract_province_territory_data": AssetIn(
            key=AssetKey("extract_province_territory_data")
        )
    },
)
def check_province_territory_data(
    context: AssetCheckExecutionContext,
    extract_province_territory_data: pd.DataFrame,
):
    """Checks if 'province_territory' data matches the data in the database."""

    return compare_uploaded_database_data(
        context,
        extract_province_territory_data,
        Province,
    )

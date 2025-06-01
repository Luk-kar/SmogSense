"""

"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)

# Pipeline
from territory.models import (
    Province,
)
from territory.assets.constants import (
    TerritoryAssetCategories as Categories,
    Groups as TerritoryGroups,
)

# Common
from common.constants import get_metadata_categories
from common.utils.database.data_ingestion import (
    upload_data_and_log_materialization,
)
from common.utils.logging import log_dataframe_info


@asset(
    group_name=TerritoryGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.TERRITORY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.JSONB,
        )
    },
)
def upload_data_province_territory(
    context: AssetExecutionContext,
    extract_province_territory_data: pd.DataFrame,
):
    """
    Upload 'province_territory' data to PostgreSQL database using bulk operations.
    """

    df = extract_province_territory_data

    log_dataframe_info(context, df, "province_territory")

    upload_data_and_log_materialization(
        context=context,
        data_frame=df,
        model_class=Province,
        asset_key_str="upload_data_province_territory",
        description="Uploaded 'province_territory' data to PostgreSQL database.",
    )

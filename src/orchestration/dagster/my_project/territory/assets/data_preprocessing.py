"""
Contains the assets for data processing of the 'social media' data.
"""

# Python
from typing import Any

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)

# Pipeline
from territory.assets.constants import (
    TerritoryAssetCategories as Categories,
    Groups as TerritoryGroups,
)

# Common
from common.constants import get_metadata_categories
from common.utils.logging import (
    log_columns_statistics,
)
from common.utils.logging import (
    log_asset_materialization,
)
from common.utils.geometry import convert_to_wkt


@asset(
    group_name=TerritoryGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.TERRITORY,
            Categories.DATA_PROCESSING,
        )
    },
)
def extract_province_territory_data(
    context: AssetExecutionContext,
    download_province_territory_data_from_minio: Any,
) -> pd.DataFrame:
    """
    Transforms downloaded 'province territory' data into a DataFrame
    The resulting DataFrame contains two columns:
      - province: The name of the province.
      - coordinates: The associated geometry coordinates.
    """
    data = download_province_territory_data_from_minio

    if "features" not in data:
        raise ValueError("Invalid data format: missing 'features' key.")

    # Build a list of rows with province names and coordinates.
    rows = []
    for feature in data["features"]:

        province = feature.get("properties", {}).get("name", "Unknown")
        coordinates = feature.get("geometry", {}).get("coordinates")

        rows.append({"province": province, "coordinates": coordinates})

    df = pd.DataFrame(rows)
    context.log.info(f"Created DataFrame with {len(df)} rows")

    log_columns_statistics(context, df)

    # Convert the 'coordinates' column to a WKT string.
    df["coordinates"] = df["coordinates"].apply(convert_to_wkt)

    context.log.info(f"Example of WKT coordinates:\n{df['coordinates'].iloc[0]} ")

    unique_provinces = df["province"].unique()
    context.log.info(f"→ Unique provinces:\n{unique_provinces}")

    log_asset_materialization(
        context=context,
        data_frame=df,
        asset_key="extract_province_territory_data",
        description="Province territory data flattened",
    )

    return df

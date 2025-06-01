"""
Contains the assets for data modeling of the 'air quality pollution map' asset.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    asset,
    AssetExecutionContext,
)

# Pipeline
from common.utils.logging import (
    log_asset_materialization,
)
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    MapPollutantGroups,
)
from common.utils.logging import (
    log_unique_values,
)
from air_quality.assets.pollution_map.assets.utils.translation import (
    translate_pollutant_names,
    translate_pollutant_name,
    translate_indicator_type,
    translate_column,
)
from air_quality.assets.pollution_map.assets.utils.geometry import (
    extract_geometry_data,
    analyze_geometry_features,
    convert_geometry_to_wkt,
)
from air_quality.assets.pollution_map.assets.utils.data_builders import (
    build_dataframe_from_pollutants,
    build_pollutant_rows,
    build_measurement_rows,
)


@asset(
    group_name=MapPollutantGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.MAP_POLLUTANT_TABLE,
        ),
    },
)
def create_dataframe_map_pollutants(
    context: AssetExecutionContext,
    download_air_quality_map_pollutant_data_from_minio: dict,
) -> pd.DataFrame:
    """
    Extracts and creates a dataframe for the 'pollutant' table.
    """

    context.log.info("➡️ Extracting pollutants data...")
    data = download_air_quality_map_pollutant_data_from_minio

    df_pollutants = build_dataframe_from_pollutants(data, build_pollutant_rows)

    log_unique_values(context, df_pollutants["pollutant_name"], "pollutants")
    log_unique_values(context, df_pollutants["indicator_type"], "indicator types")

    df_pollutants = translate_column(
        context,
        df_pollutants,
        "pollutant_name",
        translate_pollutant_name,
        "pollutant names",
    )
    df_pollutants = translate_column(
        context,
        df_pollutants,
        "indicator_type",
        translate_indicator_type,
        "indicator types",
    )

    log_asset_materialization(
        context=context,
        asset_key="create_dataframe_map_pollutants",
        data_frame=df_pollutants,
        description="Type of pollutants and their indicators...",
    )

    return df_pollutants


@asset(
    group_name=MapPollutantGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.MAP_MEASUREMENT_TABLE,
        ),
    },
)
def create_dataframe_map_measurements(
    context: AssetExecutionContext,
    download_air_quality_map_pollutant_data_from_minio: dict,
) -> pd.DataFrame:
    """
    Extracts and creates a dataframe for the 'measurements' table.
    """

    context.log.info("➡️ Extracting measurements data...")
    data = download_air_quality_map_pollutant_data_from_minio

    df_measurements = build_dataframe_from_pollutants(data, build_measurement_rows)

    log_unique_values(context, df_measurements["pollutant_name"], "pollutants")
    log_unique_values(context, df_measurements["data_year"], "years")
    log_unique_values(context, df_measurements["date_published"], "dates published")

    df_measurements = translate_column(
        context,
        df_measurements,
        "pollutant_name",
        translate_pollutant_name,
        "pollutant names",
    )

    log_asset_materialization(
        context=context,
        asset_key="create_dataframe_map_measurements",
        data_frame=df_measurements,
        description="Measurements of pollutants in a given year",
    )

    return df_measurements


@asset(
    group_name=MapPollutantGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.MAP_GEOMETRY_TABLE,
        ),
    },
)
def create_dataframe_map_geometry(
    context: AssetExecutionContext,
    download_air_quality_map_pollutant_data_from_minio: dict,
) -> pd.DataFrame:
    """
    Extracts and creates a dataframe for the 'geometry' table.
    """

    data = download_air_quality_map_pollutant_data_from_minio

    df_geometry = extract_geometry_data(context, data)

    analyze_geometry_features(context, df_geometry)

    df_geometry = translate_pollutant_names(context, df_geometry)

    df_geometry = convert_geometry_to_wkt(context, df_geometry)

    df_geometry = drop_duplicate_rows(context, df_geometry)

    log_asset_materialization(
        context=context,
        asset_key="create_dataframe_map_geometry",
        data_frame=df_geometry,
        description="Geometry of pollutants",
    )

    return df_geometry


def drop_duplicate_rows(
    context: AssetExecutionContext, df_geometry: pd.DataFrame
) -> pd.DataFrame:
    """
    Drops duplicate rows based on 'pollutant_name', 'year', and 'geometry'.
    """

    context.log.info(
        "➡️ Drop duplicate rows based on 'pollutant_name', 'year', and 'geometry'..."
    )

    get_geometry_len = len(df_geometry.index)

    df_geometry = df_geometry.drop_duplicates(
        subset=["pollutant_name", "year", "geometry"], keep="first"
    )

    context.log.info(
        f"Number of duplicate rows dropped: {get_geometry_len - len(df_geometry.index)}"
    )

    return df_geometry

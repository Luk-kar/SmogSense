"""
Data modeling assets for the 'air quality station' data.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    Failure,
    asset,
)

# Pipeline
from common.utils.dataframe import (
    apply_default_ordering,
    ensure_dataframe_columns_match_model,
)
from air_quality.models.station_models import (
    Area,
    Location,
    Province,
    Station,
)
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    StationGroups,
)
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.logging import (
    log_dataframe_info,
    log_asset_materialization,
)
from common.utils.dataframe import drop_rows_with_nulls


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.STATION_DATA,
            Categories.PROVINCE_TABLE,
        ),
    },
)
def create_dataframe_province(
    context: AssetExecutionContext,
    renaming_columns_air_quality_station_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'province' DataFrame from the sanitized 'air quality station' data."""

    try:
        df_source = renaming_columns_air_quality_station_data

        log_dataframe_info(context, df_source, "Data source")

        df_province = df_source[["province"]].drop_duplicates()

        df_province = drop_rows_with_nulls(df_province, Province)

        df_province = apply_default_ordering(df_province, Province, context)

        model_values_columns = get_model_non_primary_keys_and_non_generated_columns(
            Province
        )

        # Reorder DataFrame columns to match model columns
        df_province = df_province[model_values_columns]

        ensure_dataframe_columns_match_model(df_province, Province)

        context.log.info(
            f"'province' DataFrame created successfully.\n{df_province.head(3)}"
        )

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            asset_key="create_dataframe_province",
            description="Province DataFrame created",
            data_frame=df_province,
        )

    except Exception as e:
        context.log.error(f"Error creating 'province' DataFrame: {e}")
        raise Failure(f"Failed to create 'province' DataFrame: {e}") from e

    return df_province


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.STATION_DATA,
            Categories.AREA_TABLE,
        ),
    },
)
def create_dataframe_area(
    context: AssetExecutionContext,
    renaming_columns_air_quality_station_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'area' DataFrame from the sanitized 'air quality station' data."""

    try:
        df_source = renaming_columns_air_quality_station_data

        log_dataframe_info(context, df_source, "Data source")

        df_area = df_source[
            ["id_area", "city_district", "city", "county", "province"]
        ].drop_duplicates()

        model_values_columns = get_model_non_primary_keys_and_non_generated_columns(
            Area
        )

        context.log.info(
            f"Model values columns before swapping: {model_values_columns}"
        )

        model_values_columns = list(
            map(lambda x: "province" if x == "id_province" else x, model_values_columns)
        )

        context.log.info(f"Model values columns after swapping: {model_values_columns}")

        # Reorder DataFrame columns to match model columns
        df_area = df_area[model_values_columns]

        df_area = df_area.sort_values(by=["province"])

        context.log.info(f"'area' DataFrame created successfully.\n{df_area.head(3)}")

        log_asset_materialization(
            context=context,
            asset_key="create_dataframe_area",
            description="Area DataFrame created",
            data_frame=df_area,
        )

    except Exception as e:
        context.log.error(f"Error creating 'area' DataFrame: {e}")
        raise Failure(f"Failed to create 'area' DataFrame: {e}") from e

    return df_area


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.STATION_DATA,
            Categories.LOCATION_TABLE,
        ),
    },
)
def create_dataframe_location(
    context: AssetExecutionContext,
    renaming_columns_air_quality_station_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'location' DataFrame from the sanitized 'air quality station' data"""

    try:
        df_source = renaming_columns_air_quality_station_data

        log_dataframe_info(context, df_source, "Data source")

        df_location = df_source[
            [
                "latitude",
                "longitude",
                "id_area",
                "street_address",
            ]
        ].drop_duplicates()

        df_location = drop_rows_with_nulls(df_location, Location)

        df_location = apply_default_ordering(df_location, Location, context)

        model_values_columns = get_model_non_primary_keys_and_non_generated_columns(
            Location
        )

        # Reorder DataFrame columns to match model columns
        df_location = df_location[model_values_columns]

        ensure_dataframe_columns_match_model(df_location, Location)

        context.log.info(
            f"'location' DataFrame created successfully.\n{df_location.head(3)}"
        )

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            asset_key="create_dataframe_location",
            description="Location DataFrame created",
            data_frame=df_location,
        )

    except Exception as e:
        context.log.error(f"Error creating 'location' DataFrame: {e}")
        raise Failure(f"Failed to create 'location' DataFrame: {e}") from e

    return df_location


@asset(
    group_name=StationGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.STATION_DATA,
            Categories.STATION_TABLE,
        ),
    },
)
def create_dataframe_station(
    context: AssetExecutionContext,
    renaming_columns_air_quality_station_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'station' DataFrame from the sanitized 'air quality station' data."""

    try:
        df_source = renaming_columns_air_quality_station_data

        log_dataframe_info(context, df_source, "Data source")

        df_station = df_source[
            [
                "id_station",
                "station_name",
                # The natural foreign keys
                "latitude",
                "longitude",
                "id_area",
                "street_address",
            ]
        ].drop_duplicates()

        df_station.drop_duplicates(subset=["id_station", "station_name"], inplace=True)

        df_station = drop_rows_with_nulls(df_station, Station)

        df_station = df_station.sort_values(
            by=[
                "id_station",
                # The natural foreign keys
                "latitude",
                "longitude",
                "street_address",
            ]
        )

        context.log.info(
            f"'station' DataFrame created successfully.\n{df_station.head(3)}"
        )

        log_asset_materialization(
            context=context,
            asset_key="create_dataframe_station",
            description="Station DataFrame created",
            data_frame=df_station,
        )

    except Exception as e:
        context.log.error(f"Error creating 'station' DataFrame: {e}")
        raise Failure(f"Failed to create 'station' DataFrame: {e}") from e

    return df_station

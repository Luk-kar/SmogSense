"""
Contains the assets that are used to upload data to the PostgreSQL database.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
    AssetKey,
    asset,
    Failure,
)

# Pipeline
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
from common.utils.database.data_ingestion import (
    upload_data_and_log_materialization,
)
from common.utils.database.session_handling import get_database_session
from common.utils.database.data_preprocessing import (
    map_foreign_keys_general,
)


@asset(
    group_name=StationGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.STATION_DATA,
            Categories.PROVINCE_TABLE,
        )
    },
)
def upload_data_province(
    context: AssetExecutionContext,
    create_dataframe_province: pd.DataFrame,
):
    """Upload 'province' data to PostgreSQL database using bulk operations."""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_province,
        model_class=Province,
        asset_key_str="upload_data_province",
        description="Uploaded 'province' data to PostgreSQL database.",
    )


@asset(
    group_name=StationGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={AssetKey("upload_data_province")},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.STATION_DATA,
            Categories.AREA_TABLE,
        )
    },
)
def upload_data_area(
    context: AssetExecutionContext,
    create_dataframe_area: pd.DataFrame,
):
    """Upload 'area' data to PostgreSQL database using bulk operations."""

    with get_database_session(context) as session:

        # Retrieve the mapping of province names to id_province
        provinces = session.query(Province).all()
        province_mapping = {p.province: p.id_province for p in provinces}

        context.log.info(f"Province mapping: {province_mapping}")

        # Prepare mappings dictionary with 'province' as the key
        mappings = {"province": province_mapping}

        # Map foreign keys
        mapped_df = map_foreign_keys_general(
            create_dataframe_area.copy(), mappings, context
        )

        context.log.info(
            f"Area DataFrame after mapping id_province:\n{mapped_df.head()}"
        )

        # Proceed to upload data
        upload_data_and_log_materialization(
            context=context,
            data_frame=mapped_df,
            model_class=Area,
            asset_key_str="upload_data_area",
            description="Uploaded 'area' data to PostgreSQL database.",
        )


@asset(
    group_name=StationGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        AssetKey("upload_data_area"),
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.STATION_DATA,
            Categories.LOCATION_TABLE,
        )
    },
)
def upload_data_location(
    context: AssetExecutionContext,
    create_dataframe_location: pd.DataFrame,
):
    """Upload 'location' data to PostgreSQL database using bulk operations."""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_location,
        model_class=Location,
        asset_key_str="upload_data_location",
        description="Uploaded 'location' data to PostgreSQL database.",
    )


@asset(
    group_name=StationGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={AssetKey("upload_data_location")},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.STATION_DATA,
            Categories.STATION_TABLE,
        )
    },
)
def upload_data_station(
    context: AssetExecutionContext,
    create_dataframe_station: pd.DataFrame,
):
    """Upload 'station' data to PostgreSQL database using bulk operations."""

    with get_database_session(context) as session:

        # Retrieve the mapping of area names to id_area
        locations = session.query(Location).all()
        location_mapping = {
            l.id_location: {
                "latitude": l.latitude,
                "longitude": l.longitude,
                "id_area": l.id_area,
                "street_address": l.street_address,
            }
            for l in locations
        }

        context.log.info(f"Province mapping: {location_mapping}")

        # Map id_location to the station data
        # Assuming 'id_location' is a column in create_dataframe_station
        create_dataframe_station["id_location"] = create_dataframe_station.apply(
            lambda row: map_location(row, location_mapping), axis=1
        )

        # Check for any provinces in area data that are missing in the province mapping

        missing_locations = create_dataframe_station[
            create_dataframe_station["id_location"].isnull()
        ]["id_location"].unique()

        if len(missing_locations) > 0:
            raise Failure(f"Locations not found in database: {missing_locations}")

        # Remove 'province' column if not needed
        create_dataframe_station = create_dataframe_station.drop(
            columns=["latitude", "longitude", "id_area", "street_address"]
        )

        context.log.info(
            f"Area DataFrame after mapping id_location:\n{create_dataframe_station.head()}"
        )

        upload_data_and_log_materialization(
            context=context,
            data_frame=create_dataframe_station,
            model_class=Station,
            asset_key_str="upload_data_station",
            description="Uploaded 'station' data to PostgreSQL database.",
        )


def map_location(row: pd.Series, location_mapping: dict) -> int:
    """
    Map a row of data to an existing location in the database.
    """

    return next(
        (
            id_location
            for id_location, loc in location_mapping.items()
            if loc["latitude"] == row["latitude"]
            and loc["longitude"] == row["longitude"]
            and loc["id_area"] == row["id_area"]
            and loc["street_address"] == row["street_address"]
        ),
        None,  # Default value if no match is found
    )

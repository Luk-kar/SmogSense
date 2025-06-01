"""
Contains the assets that are used to upload 'pollutants', 'measurement', and 'geometry' data 
to the PostgreSQL database for the 'pollution map' feature.
"""

import pandas as pd
from dagster import (
    AssetExecutionContext,
    AssetKey,
    asset,
    Failure,
)

# Pipeline
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    MapPollutantGroups,
)
from common.utils.database.data_ingestion import (
    upload_data_and_log_materialization,
)
from common.utils.database.session_handling import (
    get_database_session,
)
from common.utils.database.data_preprocessing import (
    map_foreign_keys_general,
)
from air_quality.models.map_pollution_models import (
    Pollutant,
    Measurement,
)
from common.utils.logging import log_dataframe_info
from air_quality.assets.pollution_map.assets.utils.upload_geometry import (
    validate_and_rename_pollutant_column,
    fetch_mappings_from_database,
    map_geometry_to_measurements,
    upload_geometry_data_to_database,
)


@asset(
    group_name=MapPollutantGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.MAP_POLLUTANT_TABLE,
        )
    },
)
def upload_data_map_pollutants(
    context: AssetExecutionContext,
    create_dataframe_map_pollutants: pd.DataFrame,
):
    """
    Upload 'pollutants' data to PostgreSQL database using bulk operations.
    Expects create_dataframe_map_pollutants DataFrame with columns:
        - pollutant_name
        - indicator_name

    The id column 'id_pollutant' is automatically generated.
    """

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_map_pollutants,
        model_class=Pollutant,
        asset_key_str="upload_data_map_pollutants",
        description="Uploaded 'pollutants' data to PostgreSQL database.",
    )


@asset(
    group_name=MapPollutantGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={AssetKey("upload_data_map_pollutants")},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.MAP_MEASUREMENT_TABLE,
        )
    },
)
def upload_data_map_measurements(
    context: AssetExecutionContext,
    create_dataframe_map_measurements: pd.DataFrame,
):
    """
    Upload 'measurement' data to PostgreSQL database using bulk operations.
    Expects create_dataframe_map_measurements DataFrame with columns:
        - pollutant_name (to map to id_pollutant)
        - data_year
        - date_published (date)

    The id column 'id_measurement' is automatically generated.
    """

    with get_database_session(context) as session:

        log_dataframe_info(
            context,
            create_dataframe_map_measurements,
            "create_dataframe_map_measurements",
        )

        context.log.info(
            "➡️ Retrieve existing pollutants to map pollutant_name -> id_pollutant"
        )
        pollutants = session.query(Pollutant).all()
        pollutant_mapping = {p.pollutant_name: p.id_pollutant for p in pollutants}
        context.log.info(f"pollutant mapping:\n{pollutant_mapping}")

        context.log.info(
            "➡️ Rename pollutant_name to pollutant to create right id column"
        )
        create_dataframe_map_measurements = create_dataframe_map_measurements.rename(
            columns={"pollutant_name": "pollutant"}
        )

        context.log.info(
            "columns in create_dataframe_map_measurements:\n"
            f"{create_dataframe_map_measurements.columns}"
        )

        context.log.info("➡️ Map foreign keys from pollutant_name to id_pollutant")
        mappings = {"pollutant": pollutant_mapping}
        mapped_df = map_foreign_keys_general(
            create_dataframe_map_measurements.copy(), mappings, context
        )

        context.log.info(f"columns in mapped_df:\n{mapped_df.columns}")

        context.log.info("➡️ Check if all pollutants are mapped")
        missing_pollutants = mapped_df[mapped_df["id_pollutant"].isnull()][
            "id_pollutant"
        ].unique()
        if len(missing_pollutants) > 0:
            raise Failure(
                f"❌ Some pollutants not found in the database: {missing_pollutants}"
            )

        context.log.info("➡️ Change order of columns to match the table")
        mapped_df = mapped_df[
            [
                "id_pollutant",
                "data_year",
                "date_published",
            ]
        ]

        context.log.info(f"New order of columns:\n{mapped_df.columns}")

        context.log.info("➡️ Upload data to database")

        upload_data_and_log_materialization(
            context=context,
            data_frame=mapped_df,
            model_class=Measurement,
            asset_key_str="upload_data_map_measurements",
            description="Uploaded 'measurement' data to PostgreSQL database.",
        )


@asset(
    group_name=MapPollutantGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={AssetKey("upload_data_map_measurements")},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.MAP_GEOMETRY_TABLE,
        )
    },
)
def upload_data_map_geometry(
    context: AssetExecutionContext,
    create_dataframe_map_geometry: pd.DataFrame,
):
    """
    Upload 'geometry' data to the PostgreSQL database using bulk operations.

    This asset expects create_dataframe_map_geometry DataFrame with columns:
        - geometry (e.g. WKT format)
        - value (integer)
        - pollutant_name (to map to id_pollutant)
        - year (for mapping to measurements)

    The 'id_geometry' primary key is automatically generated by the database.
    """
    with get_database_session(context) as session:

        log_dataframe_info(
            context, create_dataframe_map_geometry, "create_dataframe_map_geometry"
        )

        renamed_geometry_df = validate_and_rename_pollutant_column(
            context, create_dataframe_map_geometry
        )

        pollutant_mapping, measurement_mapping = fetch_mappings_from_database(
            context, session
        )

        mapped_geometry_df = map_geometry_to_measurements(
            context,
            renamed_geometry_df,
            pollutant_mapping,
            measurement_mapping,
        )

        upload_geometry_data_to_database(context, mapped_geometry_df)

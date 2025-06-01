"""
Functions for uploading geometry data to the database.
"""

import pandas as pd
from dagster import (
    AssetExecutionContext,
    Failure,
)

# Pipeline
from air_quality.models.map_pollution_models import (
    Pollutant,
    Measurement,
    GeometryRecord,
)
from common.utils.database.data_ingestion import upload_data_asset
from common.utils.logging import (
    log_asset_materialization,
)


def validate_and_rename_pollutant_column(
    context: AssetExecutionContext, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Validate and preprocess the geometry DataFrame.
    """

    context.log.info("➡️ Validating and renaming pollutant column...")

    if "pollutant_name" not in df.columns:
        raise Failure(
            "Expected 'pollutant_name' in geometry DataFrame to map foreign keys."
        )

    df = df.rename(columns={"pollutant_name": "pollutant"})

    context.log.info(f"DataFrame after renaming: {df.columns}")

    return df


def fetch_mappings_from_database(
    context: AssetExecutionContext, session
) -> tuple[dict, dict]:
    """
    Create mappings for pollutants and measurements from the database.

    Returns:
        pollutant_mapping: Dict mapping pollutant_name -> id_pollutant.
        measurement_mapping: Dict mapping (id_pollutant, data_year) -> id_measurement.
    """

    context.log.info(
        "➡️ Fetching pollutant and measurement mappings from the database..."
    )
    # Pollutant mapping
    pollutants = session.query(Pollutant).all()
    pollutant_mapping = {p.pollutant_name: p.id_pollutant for p in pollutants}
    context.log.info(f"Pollutant mapping: {pollutant_mapping}")

    # Measurement mapping
    measurements = session.query(Measurement).all()
    measurement_mapping = {
        (m.id_pollutant, m.data_year): m.id_measurement for m in measurements
    }
    context.log.info(f"Measurement mapping: {measurement_mapping}")

    return pollutant_mapping, measurement_mapping


def map_geometry_to_measurements(
    context: AssetExecutionContext,
    df: pd.DataFrame,
    pollutant_mapping: dict,
    measurement_mapping: dict,
) -> pd.DataFrame:
    """
    Map each row of the geometry DataFrame to its corresponding measurement_id.

    Args:
        df: The geometry DataFrame.
        pollutant_mapping: Dict mapping pollutant_name -> id_pollutant.
        measurement_mapping: Dict mapping (id_pollutant, data_year) -> id_measurement.
    Returns:
        Updated DataFrame with 'id_measurement' mapped.
    """

    context.log.info("➡️ Mapping geometry to measurements...")

    def map_to_measurement_id(row):
        p_id = pollutant_mapping.get(row["pollutant"])
        d_year = row["year"]
        return measurement_mapping.get((p_id, d_year))

    df["id_measurement"] = df.apply(map_to_measurement_id, axis=1)

    if df["id_measurement"].isnull().any():
        context.log.warning(
            "Some rows in create_dataframe_map_geometry could not be mapped to id_measurement."
        )

    # Drop unnecessary columns
    df = df.drop(columns=["year", "pollutant"])
    context.log.info(f"DataFrame after mapping: {df.head()}")

    return df


def upload_geometry_data_to_database(context: AssetExecutionContext, df: pd.DataFrame):
    """
    Upload the processed geometry data to the database.
    """

    context.log.info("➡️ Uploading geometry data to the database...")

    upload_data_asset(
        context=context,
        data_frame=df,
        model_class=GeometryRecord,
        mode="copy",  # Speeds up insert operations
    )
    log_asset_materialization(
        context=context,
        asset_key="upload_data_map_measurements",
        data_frame=df,
        description="Uploaded 'measurement' data to PostgreSQL database.",
    )

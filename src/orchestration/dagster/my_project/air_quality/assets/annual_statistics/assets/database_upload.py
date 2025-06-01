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
from air_quality.models.annual_statistics_models import (
    Province,
    ZoneType,
    Zone,
    Station,
    Indicator,
    TimeAveraging,
    Measurement,
)
from common.utils.database.data_ingestion import upload_data_asset
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    AnnualStatisticsGroups,
)
from common.utils.logging import log_asset_materialization
from common.utils.database.data_ingestion import (
    upload_data_and_log_materialization,
)
from common.utils.database.session_handling import get_database_session
from common.utils.database.data_preprocessing import map_foreign_keys_general


@asset(
    group_name=AnnualStatisticsGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.PROVINCE_TABLE,
        )
    },
)
def upload_data_province_annual_statistics(
    context: AssetExecutionContext,
    create_dataframe_province_annual_statistics: pd.DataFrame,
):
    """Upload 'province' data to PostgreSQL database using bulk operations."""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_province_annual_statistics,
        model_class=Province,
        asset_key_str="upload_data_province_annual_statistics",
        description="Uploaded 'province' data to PostgreSQL database.",
    )


@asset(
    group_name=AnnualStatisticsGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.ZONE_TYPE_TABLE,
        )
    },
)
def upload_data_zone_type(
    context: AssetExecutionContext,
    create_dataframe_zone_type: pd.DataFrame,
):
    """Upload 'zone_type' data to PostgreSQL database using bulk operations."""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_zone_type,
        model_class=ZoneType,
        asset_key_str="upload_data_zone_type",
        description="Uploaded 'zone_type' data to PostgreSQL database.",
    )


@asset(
    group_name=AnnualStatisticsGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        AssetKey("upload_data_province_annual_statistics"),
        AssetKey("upload_data_zone_type"),
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.ZONE_TABLE,
        )
    },
)
def upload_data_zone(
    context: AssetExecutionContext,
    create_dataframe_zone: pd.DataFrame,
):
    """Upload 'zone' data to PostgreSQL database using bulk operations."""

    with get_database_session(context) as session:

        # Retrieve the mapping of province names to id_province
        provinces = session.query(Province).all()
        provinces = session.query(Province).all()
        province_mapping = {p.province: p.id_province for p in provinces}

        zone_types = session.query(ZoneType).all()
        zone_type_mapping = {z.zone_type: z.id_zone_type for z in zone_types}

        # Prepare mappings dictionary
        mappings = {
            "province": province_mapping,
            "zone_type": zone_type_mapping,
        }

        # Map foreign keys
        mapped_df = map_foreign_keys_general(
            create_dataframe_zone.copy(), mappings, context
        )

        context.log.info(
            f"Zone DataFrame after mapping id_zone_type:\n{mapped_df.head()}"
        )

        upload_data_asset(
            context=context,
            data_frame=mapped_df,
            model_class=Zone,
        )

    log_asset_materialization(
        context=context,
        asset_key="upload_data_zone",
        data_frame=mapped_df,
        description="Uploaded 'zone' data to PostgreSQL database.",
    )


@asset(
    group_name=AnnualStatisticsGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={AssetKey("upload_data_zone")},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.STATION_TABLE,
        )
    },
)
def upload_data_station_annual_statistics(
    context: AssetExecutionContext,
    create_dataframe_station_annual_statistics: pd.DataFrame,
):
    """Upload 'station' data to PostgreSQL database using bulk operations."""

    with get_database_session(context) as session:

        # Retrieve mappings
        zones = session.query(Zone).all()
        zone_mapping = {z.zone_code: z.id_zone for z in zones}

        # Prepare mappings dictionary
        mappings = {
            "zone_code": zone_mapping,
        }

        # Map foreign keys
        mapped_df = map_foreign_keys_general(
            create_dataframe_station_annual_statistics.copy(), mappings, context
        )

        mapped_df = mapped_df.rename(columns={"id_zone_code": "id_zone"})

        context.log.info(
            ("Station DataFrame after mapping id_zone:\n" f"{mapped_df.head(3)}")
        )

        upload_data_asset(
            context=context,
            data_frame=mapped_df,
            model_class=Station,
        )

    log_asset_materialization(
        context=context,
        asset_key="upload_data_station_annual_statistics",
        data_frame=mapped_df,
        description="Uploaded 'station' data to PostgreSQL database.",
    )


@asset(
    group_name=AnnualStatisticsGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.INDICATOR_TABLE,
        )
    },
)
def upload_data_indicator(
    context: AssetExecutionContext,
    create_dataframe_indicator: pd.DataFrame,
):
    """Upload 'indicator' data to PostgreSQL database using bulk operations."""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_indicator,
        model_class=Indicator,
        asset_key_str="upload_data_indicator",
        description="Uploaded 'indicator' data to PostgreSQL database.",
    )


@asset(
    group_name=AnnualStatisticsGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.TIME_AVERAGING_TABLE,
        )
    },
)
def upload_data_time_averaging(
    context: AssetExecutionContext,
    create_dataframe_time_averaging: pd.DataFrame,
):
    """Upload 'time_averaging' data to PostgreSQL database using bulk operations."""

    upload_data_and_log_materialization(
        context=context,
        data_frame=create_dataframe_time_averaging,
        model_class=TimeAveraging,
        asset_key_str="upload_data_time_averaging",
        description="Uploaded 'time_averaging' data to PostgreSQL database.",
    )


@asset(
    group_name=AnnualStatisticsGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        AssetKey("upload_data_station_annual_statistics"),
        AssetKey("upload_data_indicator"),
        AssetKey("upload_data_time_averaging"),
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATABASE,
            Categories.DATABASE_FACT_TABLE,
            Categories.DATABASE_NORMALIZED,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.MEASUREMENT_TABLE,
        )
    },
)
def upload_data_measurement(
    context: AssetExecutionContext,
    create_dataframe_measurement: pd.DataFrame,
):
    """Upload 'measurement' data to PostgreSQL database using bulk operations."""

    with get_database_session(context) as session:

        station_mapping, indicator_mapping, time_averaging_mapping = (
            get_foreign_key_mappings(session)
        )

        context.log.info(f"Station mapping: {station_mapping}")
        context.log.info(f"Indicator mapping: {indicator_mapping}")
        context.log.info(f"Time averaging mapping: {time_averaging_mapping}")

        df = map_foreign_keys(
            create_dataframe_measurement.copy(),
            station_mapping,
            indicator_mapping,
            time_averaging_mapping,
        )

        check_missing_mappings(df)

        df = df.drop(
            columns=[
                "station_code",
                "zone_code",
                "indicator_type",
                "time_averaging",
            ]
        )

        # Log final DataFrame state
        context.log.info(
            "Measurement DataFrame after mapping foreign keys:\n" f"{df.head(3)}"
        )
        context.log.info(f"Columns in Measurement DataFrame: {df.columns}")

        upload_data_asset(
            context=context,
            data_frame=df,
            model_class=Measurement,
            # To speed up the process, but harder to debug and
            # do not automatically resolve the errors
            mode="copy",
        )

    log_asset_materialization(
        context=context,
        asset_key="upload_data_measurement",
        data_frame=df,
        description="Uploaded 'measurement' data to PostgreSQL database.",
    )


def get_foreign_key_mappings(session):
    """Retrieve mappings for foreign keys from the database."""
    # Retrieve data from the database
    stations = session.query(Station).all()
    zones = session.query(Zone).all()
    indicators = session.query(Indicator).all()
    time_averaging_list = session.query(TimeAveraging).all()

    # Create mappings
    id_zone_to_zone_code = {z.id_zone: z.zone_code for z in zones}
    station_mapping = {
        (s.station_code, id_zone_to_zone_code[s.id_zone]): s.id_station
        for s in stations
    }
    indicator_mapping = {i.name: i.id_indicator for i in indicators}
    time_averaging_mapping = {
        t.time_averaging: t.id_time_averaging for t in time_averaging_list
    }

    return station_mapping, indicator_mapping, time_averaging_mapping


def map_foreign_keys(df, station_mapping, indicator_mapping, time_averaging_mapping):
    """Map foreign keys in the DataFrame using the retrieved mappings."""
    # Map 'id_station'
    df["id_station"] = df.apply(
        lambda row: station_mapping.get((row["station_code"], row["zone_code"])),
        axis=1,
    )

    # Map 'id_indicator'
    df["id_indicator"] = df["indicator_type"].map(indicator_mapping)

    # Map 'id_time_averaging'
    df["id_time_averaging"] = df["time_averaging"].map(time_averaging_mapping)

    return df


def check_missing_mappings(df):
    """Check for any missing mappings in the DataFrame."""
    # Check for missing 'id_station'
    missing_stations = df[df["id_station"].isnull()][
        ["station_code", "zone_code"]
    ].drop_duplicates()
    if not missing_stations.empty:
        raise Failure(f"Stations not found in database: {missing_stations}")

    # Check for missing 'id_indicator'
    missing_indicators = df[df["id_indicator"].isnull()]["indicator_type"].unique()
    if len(missing_indicators) > 0:
        raise Failure(f"Indicators not found in database: {missing_indicators}")

    # Check for missing 'id_time_averaging'
    missing_time_averaging = df[df["id_time_averaging"].isnull()][
        "time_averaging"
    ].unique()
    if len(missing_time_averaging) > 0:
        raise Failure(
            f"Time averaging values not found in database: {missing_time_averaging}"
        )

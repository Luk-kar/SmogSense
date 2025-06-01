"""
Contains the assets that are used to upload health data (provinces, death_illness, measurement)
to the PostgreSQL database. It uses the 'extract_and_format_health_data' asset as input.
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

# Local imports
from common.utils.database.session_handling import get_database_session
from common.utils.database.data_ingestion import (
    upload_data_and_log_materialization,
)
from common.utils.logging import log_dataframe_info
from common.constants import get_metadata_categories
from health.models.health_models import (
    Province,
    DeathIllness,
    Measurement,
    CountryPopulation,
    ProvincePopulation,
)
from health.constants import (
    HealthGroups,
    HealthAssetCategories as Categories,
)


@asset(
    group_name=HealthGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.PROVINCE,
        )
    },
)
def upload_data_health_provinces(
    context: AssetExecutionContext,
    lower_characters_in_province_column: pd.DataFrame,
):
    """
    Upload provinces data to the PostgreSQL database (health_data.provinces).
    """

    provinces_df = lower_characters_in_province_column

    log_dataframe_info(context, provinces_df, "provinces_df")

    if provinces_df.empty:
        raise Failure(
            ("❌ No province data found to upload." "`provinces_df` is empty.")
        )

    context.log.info(f"➡️ Uploading {len(provinces_df)} province records.")

    upload_data_and_log_materialization(
        context=context,
        data_frame=provinces_df,
        model_class=Province,
        asset_key_str="upload_data_health_provinces",
        description="Uploaded 'province' data to PostgreSQL database.",
        mode="copy",
    )


@asset(
    group_name=HealthGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.DEATH_ILLNESS,
        )
    },
)
def upload_data_health_death_illness(
    context: AssetExecutionContext,
    rename_columns_death_illness_data: pd.DataFrame,
):
    """
    Upload death_illness data to the PostgreSQL database (health_data.death_illness).
    """

    illness_df = rename_columns_death_illness_data

    log_dataframe_info(context, illness_df, "illness_df")

    if illness_df.empty:
        raise Failure("❌ No illness data found to upload. Skipping.")

    context.log.info(f"➡️ Uploading {len(illness_df)} death illness records.")

    upload_data_and_log_materialization(
        context=context,
        data_frame=illness_df,
        model_class=DeathIllness,
        asset_key_str="upload_data_health_death_illness",
        description="Uploaded 'death_illness' data to PostgreSQL database.",
        mode="copy",
    )


@asset(
    group_name=HealthGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        AssetKey(
            "upload_data_health_death_illness",
        ),
        AssetKey("upload_data_health_provinces"),
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.MEASUREMENT,
        )
    },
)
def upload_data_health_measurement(
    context: AssetExecutionContext,
    rename_columns_measurement_data: pd.DataFrame,
):
    """
    Upload measurement data to the PostgreSQL database (health_data.measurement).
    """

    measurement_df = rename_columns_measurement_data

    log_dataframe_info(context, measurement_df, "measurement_df")

    if measurement_df.empty:
        raise Failure("❌ No measurement data found to upload. Skipping.")

    # Before upload, we may optionally verify foreign key consistency.
    # For example, we can ensure that 'id_province' values exist in the provinces table,
    # or 'id_illness' values exist in the death_illness table.

    with get_database_session(context) as session:

        # Validate province IDs

        existing_provinces = {
            p.id_province for p in session.query(Province.id_province).all()
        }

        invalid_provinces = set(measurement_df["id_province"]) - existing_provinces

        if invalid_provinces:
            raise Failure(
                f"❌ Cannot upload measurements. Unknown province IDs: {invalid_provinces}"
            )

        # Validate illness IDs

        existing_illnesses = {
            d.id_illness for d in session.query(DeathIllness.id_illness).all()
        }

        invalid_illnesses = set(measurement_df["id_illness"]) - existing_illnesses

        if invalid_illnesses:
            raise Failure(
                f"❌ Cannot upload measurements. Unknown illness IDs: {invalid_illnesses}"
            )

    context.log.info(f"➡️ Uploading {len(measurement_df)} measurement records.")

    upload_data_and_log_materialization(
        context=context,
        data_frame=measurement_df,
        model_class=Measurement,
        asset_key_str="upload_data_health_measurement",
        description="Uploaded 'measurement' data to PostgreSQL database.",
    )


@asset(
    group_name=HealthGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.COUNTRY,
        )
    },
)
def upload_data_health_population_country(
    context: AssetExecutionContext,
    extract_and_format_country_people_total_data: pd.DataFrame,
):
    """
    Uploads country-level population data to the PostgreSQL database (health_dim.country_population).
    """

    country_df = extract_and_format_country_people_total_data

    log_dataframe_info(context, country_df, "country_df")

    if country_df.empty:
        raise Failure("❌ No country population data found to upload.")

    context.log.info(f"➡️ Uploading {len(country_df)} country population records.")

    upload_data_and_log_materialization(
        context=context,
        data_frame=country_df,
        model_class=CountryPopulation,
        asset_key_str="upload_data_health_country_population",
        description="Uploaded 'country_population' data to PostgreSQL database.",
        mode="update_non_id_values",
    )


@asset(
    group_name=HealthGroups.DATABASE_UPLOAD,
    required_resource_keys={"postgres_alchemy"},
    non_argument_deps={
        AssetKey(
            "upload_data_health_provinces",
        )
    },
    metadata={
        "categories": get_metadata_categories(
            Categories.HEALTH_DATA,
            Categories.DATABASE,
            Categories.DATABASE_INIT_TABLE,
            Categories.PROVINCE,
        )
    },
)
def upload_data_health_population_province(
    context: AssetExecutionContext,
    extract_and_format_province_people_total_data: pd.DataFrame,
):
    """
    Uploads province-level population data to the PostgreSQL database (health_dim.province_population).
    """

    province_df = extract_and_format_province_people_total_data

    log_dataframe_info(context, province_df, "province_df")

    # Get province ID mapping from the database
    with get_database_session(context) as session:
        provinces = session.query(Province.id_province, Province.province).all()
        province_id_map = {province: id_province for id_province, province in provinces}

    # Display mapping
    context.log.info(f"Province ID mapping:\n{province_id_map}")

    # Add id_province column using the mapping
    province_df["id_province"] = (
        province_df["province"].str.lower().map(province_id_map)
    )

    # Validate mappings
    missing_provinces = province_df[province_df["id_province"].isna()][
        "province"
    ].unique()
    if len(missing_provinces) > 0:
        raise Failure(f"❌ Missing province IDs for: {', '.join(missing_provinces)}")

    # Select only columns needed for ProvincePopulation
    final_df = province_df[["id_province", "year", "people_total"]]

    log_dataframe_info(context, final_df, "final_df")

    upload_data_and_log_materialization(
        context=context,
        data_frame=final_df,
        model_class=ProvincePopulation,
        asset_key_str="upload_data_health_province_population",
        description="Uploaded 'province_population' data to PostgreSQL database.",
        mode="update_non_id_values",
    )

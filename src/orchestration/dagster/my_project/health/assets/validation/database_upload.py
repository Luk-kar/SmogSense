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
from health.models.health_models import (
    Province,
    DeathIllness,
    Measurement,
    ProvincePopulation,
    CountryPopulation,
)
from common.utils.database.data_validation import (
    compare_uploaded_database_data,
)


@asset_check(
    asset=AssetKey("upload_data_health_provinces"),
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "dataframe_province": AssetIn(
            key=AssetKey("lower_characters_in_province_column")
        )
    },
)
def check_province_data(
    context: AssetCheckExecutionContext,
    dataframe_province: pd.DataFrame,
):
    """Checks if 'province' data matches the data in the database."""

    return compare_uploaded_database_data(context, dataframe_province, Province)


@asset_check(
    asset=AssetKey("upload_data_health_death_illness"),
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "dataframe_death_illness": AssetIn(
            key=AssetKey("rename_columns_death_illness_data")
        )
    },
)
def check_death_illness_data(
    context: AssetCheckExecutionContext,
    dataframe_death_illness: pd.DataFrame,
):
    """Checks if 'death_illness' data matches the data in the database."""

    return compare_uploaded_database_data(
        context, dataframe_death_illness, DeathIllness
    )


@asset_check(
    asset=AssetKey("upload_data_health_measurement"),
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "dataframe_measurements": AssetIn(
            key=AssetKey("rename_columns_measurement_data")
        )
    },
)
def check_measurement_data(
    context: AssetCheckExecutionContext,
    dataframe_measurements: pd.DataFrame,
):
    """Checks if 'measurement' data matches the data in the database."""

    return compare_uploaded_database_data(context, dataframe_measurements, Measurement)


@asset_check(
    asset=AssetKey("upload_data_health_population_country"),
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "dataframe_country_population": AssetIn(
            key=AssetKey("extract_and_format_country_people_total_data")
        )
    },
)
def check_country_population_data(
    context: AssetCheckExecutionContext,
    dataframe_country_population: pd.DataFrame,
):
    """Checks if 'country_population' data matches the data in the database."""

    return compare_uploaded_database_data(
        context, dataframe_country_population, CountryPopulation
    )


@asset_check(
    asset=AssetKey("upload_data_health_population_province"),
    required_resource_keys={"postgres_alchemy"},
    additional_ins={
        "dataframe_province_population": AssetIn(
            key=AssetKey("extract_and_format_province_people_total_data")
        )
    },
)
def check_province_population_data(
    context: AssetCheckExecutionContext,
    dataframe_province_population: pd.DataFrame,
):
    """Checks if 'province_population' data matches the data in the database."""

    return compare_uploaded_database_data(
        context, dataframe_province_population, ProvincePopulation
    )

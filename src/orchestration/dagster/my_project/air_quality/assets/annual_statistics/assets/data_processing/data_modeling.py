"""
Data modeling assets for the 'air quality annual statistics' data.
"""

# Third-party
import pandas as pd
from typing import List, Type

# Dagster
from dagster import (
    AssetExecutionContext,
    Failure,
    asset,
)

# SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta

# Pipeline
from common.utils.dataframe import (
    apply_default_ordering,
)
from air_quality.models.annual_statistics_models import (
    Province,
    ZoneType,
    Zone,
    Station,
    Indicator,
    TimeAveraging,
    Measurement,
)
from common.constants import get_metadata_categories
from air_quality.assets.constants import (
    AirQualityAssetCategories as Categories,
    AnnualStatisticsGroups,
)
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.logging import log_asset_materialization
from common.utils.dataframe import (
    change_dataframe_column_types,
    replace_greek_mu_with_micro_character,
    drop_rows_with_nulls,
)
from common.utils.logging import log_dataframe_info


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.PROVINCE_TABLE,
        ),
    },
)
def create_dataframe_province_annual_statistics(
    context: AssetExecutionContext,
    rename_columns_and_values_air_quality_annual_statistics_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'province' DataFrame from the sanitized 'air quality annual statistics' data."""
    try:
        df_source = rename_columns_and_values_air_quality_annual_statistics_data

        log_dataframe_info(context, df_source, "Data source")

        df_province = prepare_dataframe(
            context=context,
            df_source=df_source,
            columns=["province"],
            model_class=Province,
            df_name="province",
        )

        log_asset_materialization(
            context=context,
            data_frame=df_province,
            asset_key="create_dataframe_province_annual_statistics",
            description="Province DataFrame created",
        )

        return df_province

    except Exception as e:

        raise Failure(f"Failed to create 'province' DataFrame: {e}") from e


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.ZONE_TYPE_TABLE,
        ),
    },
)
def create_dataframe_zone_type(
    context: AssetExecutionContext,
    rename_columns_and_values_air_quality_annual_statistics_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'zone_type' DataFrame from the sanitized 'air quality annual statistics' data."""
    try:
        df_source = rename_columns_and_values_air_quality_annual_statistics_data

        log_dataframe_info(context, df_source, "Data source")

        df_zone_type = prepare_dataframe(
            context=context,
            df_source=df_source,
            columns=["zone_type"],
            model_class=ZoneType,
            df_name="zone_type",
        )

        log_asset_materialization(
            context=context,
            data_frame=df_zone_type,
            asset_key="create_dataframe_zone_type",
            description="ZoneType DataFrame created",
        )

        return df_zone_type

    except Exception as e:

        raise Failure(f"Failed to create 'zone_type' DataFrame: {e}") from e


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.ZONE_TABLE,
        ),
    },
)
def create_dataframe_zone(
    context: AssetExecutionContext,
    rename_columns_and_values_air_quality_annual_statistics_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'zone' DataFrame from the sanitized 'air quality annual statistics' data."""
    try:
        df_source = rename_columns_and_values_air_quality_annual_statistics_data

        log_dataframe_info(context, df_source, "Data source")

        # Extract relevant columns
        df_zone = df_source[
            ["zone_code", "zone_name", "zone_type", "province"]
        ].drop_duplicates()

        # Check if all zone_code are unique
        if df_zone["zone_code"].nunique() != len(df_zone):
            raise ValueError("Not all 'zone_code' values are unique.")

        df_zone = drop_rows_with_nulls(df_zone, Zone)

        df_zone = df_zone.sort_values(by=["zone_name", "zone_type", "province"])

        context.log.info(f"'zone' DataFrame created successfully.\n{df_zone.head(3)}")

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            data_frame=df_zone,
            asset_key="create_dataframe_zone",
            description="Zone DataFrame created",
        )

        return df_zone

    except Exception as e:

        raise Failure(f"Failed to create 'zone' DataFrame: {e}") from e


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.STATION_TABLE,
        ),
    },
)
def create_dataframe_station_annual_statistics(
    context: AssetExecutionContext,
    rename_columns_and_values_air_quality_annual_statistics_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'station' DataFrame from the sanitized 'air quality annual statistics' data."""
    try:
        df_source = rename_columns_and_values_air_quality_annual_statistics_data

        log_dataframe_info(context, df_source, "Data source")

        # Extract relevant columns
        df_station = df_source[["station_code", "zone_code"]].drop_duplicates()

        df_station = df_station.drop_duplicates(subset=["station_code", "zone_code"])

        df_station = drop_rows_with_nulls(df_station, Station)

        df_station = df_station.sort_values(by=["station_code", "zone_code"])

        context.log.info(
            f"'station' DataFrame created successfully.\n{df_station.head(3)}"
        )

        log_asset_materialization(
            context=context,
            data_frame=df_station,
            asset_key="create_dataframe_station_annual_statistics",
            description="Station DataFrame created",
        )

        return df_station

    except Exception as e:

        raise Failure(f"Failed to create 'station' DataFrame: {e}") from e


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.INDICATOR_TABLE,
        ),
    },
)
def create_dataframe_indicator(
    context: AssetExecutionContext,
    rename_columns_and_values_air_quality_annual_statistics_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'indicator' DataFrame from the sanitized 'air quality annual statistics' data."""
    try:
        df_source = rename_columns_and_values_air_quality_annual_statistics_data

        log_dataframe_info(context, df_source, "Data source")

        df_indicator = pd.DataFrame()

        context.log.info("Adding 'indicator_code' column.")

        df_indicator["name"] = df_source["indicator_type"].drop_duplicates()

        context.log.info(f"Unique 'name' values:\n{df_indicator['name']}")

        description_mapping = {
            "SO2": "Sulfur dioxide, a significant air pollutant primarily produced from burning fossil fuels.",
            "NO2": "Nitrogen dioxide, a harmful gas resulting from vehicle emissions and industrial processes.",
            "NOx": "Oxides of nitrogen, a group of gases including NO and NO2, contributing to smog and acid rain.",
            "CO": "Carbon monoxide, a colorless, odorless gas emitted from vehicle exhaust and incomplete combustion.",
            "O3": "Ozone, a secondary pollutant formed by the reaction of sunlight with pollutants like NOx and VOCs.",
            "C6H6": "Benzene, a volatile organic compound and known carcinogen found in industrial emissions.",
            "PM10": "Particulate matter with a diameter of 10 micrometers or less, harmful to respiratory health.",
            "PM2.5": "Fine particulate matter with a diameter of 2.5 micrometers or less, deeply penetrates the lungs.",
            "Pb(PM10)": "Lead in PM10 particles, a toxic metal affecting the nervous system and cognitive function.",
            "As(PM10)": "Arsenic in PM10 particles, a carcinogenic metal that poses severe health risks.",
            "Cd(PM10)": "Cadmium in PM10 particles, a toxic metal causing kidney damage and other health issues.",
            "Ni(PM10)": "Nickel in PM10 particles, a heavy metal linked to respiratory and cardiovascular problems.",
            "BaP(PM10)": "Benzo[a]pyrene in PM10 particles, a polycyclic aromatic hydrocarbon and potent carcinogen.",
            "BkF(PM10)": "Benzo[k]fluoranthene in PM10 particles, a polycyclic aromatic hydrocarbon with carcinogenic properties.",
            "IP(PM10)": "Indeno[1,2,3-cd]pyrene in PM10 particles, a polycyclic aromatic hydrocarbon linked to cancer.",
            "DBahA(PM10)": "Dibenz[a,h]anthracene in PM10 particles, a polycyclic aromatic hydrocarbon with carcinogenic properties.",
            "BjF(PM10)": "Benzo[j]fluoranthene in PM10 particles, a polycyclic aromatic hydrocarbon and potential carcinogen.",
            "BbF(PM10)": "Benzo[b]fluoranthene in PM10 particles, a polycyclic aromatic hydrocarbon linked to cancer.",
            "BaA(PM10)": "Benzo[a]anthracene in PM10 particles, a polycyclic aromatic hydrocarbon and known carcinogen.",
            "Ca2+(PM2.5)": "Calcium ions in PM2.5 particles, often associated with soil dust and construction activities.",
            "SO42_(PM2.5)": "Sulfate ions in PM2.5 particles, formed from sulfur dioxide and contributing to acid rain.",
            "OC(PM2.5)": "Organic carbon in PM2.5 particles, derived from combustion processes and natural sources.",
            "NO3_(PM2.5)": "Nitrate ions in PM2.5 particles, formed from nitrogen oxides and contributing to air pollution.",
            "NH4+(PM2.5)": "Ammonium ions in PM2.5 particles, often associated with agricultural emissions.",
            "Na+(PM2.5)": "Sodium ions in PM2.5 particles, commonly originating from sea salt and industrial processes.",
            "Mg2+(PM2.5)": "Magnesium ions in PM2.5 particles, derived from soil dust and natural sources.",
            "K+(PM2.5)": "Potassium ions in PM2.5 particles, linked to biomass burning and soil dust.",
            "EC(PM2.5)": "Elemental carbon in PM2.5 particles, a component of soot from combustion processes.",
            "Cl_(PM2.5)": "Chloride ions in PM2.5 particles, often from sea spray or industrial sources.",
            "Hg(TGM)": "Mercury in total gaseous form, a toxic heavy metal with long-range atmospheric transport.",
            "formaldehyde": "Formaldehyde, a volatile organic compound emitted from industrial processes and combustion.",
            "BkF(dust_deposition)": "Benzo[k]fluoranthene in dust deposition, a carcinogenic polycyclic aromatic hydrocarbon.",
            "BjF(dust_deposition)": "Benzo[j]fluoranthene in dust deposition, a potential carcinogen among polycyclic aromatic hydrocarbons.",
            "BbF(dust_deposition)": "Benzo[b]fluoranthene in dust deposition, a carcinogenic polycyclic aromatic hydrocarbon.",
            "BaP(dust_deposition)": "Benzo[a]pyrene in dust deposition, a potent carcinogen among polycyclic aromatic hydrocarbons.",
            "BaA(dust_deposition)": "Benzo[a]anthracene in dust deposition, a known carcinogen among polycyclic aromatic hydrocarbons.",
            "As(dust_deposition)": "Arsenic in dust deposition, a toxic and carcinogenic metal.",
            "Ni(dust_deposition)": "Nickel in dust deposition, a heavy metal linked to respiratory and cardiovascular problems.",
            "IP(dust_deposition)": "Indeno[1,2,3-cd]pyrene in dust deposition, a carcinogenic polycyclic aromatic hydrocarbon.",
            "Hg(dust_deposition)": "Mercury in dust deposition, a toxic heavy metal affecting the nervous system.",
            "DBahA(dust_deposition)": "Dibenz[a,h]anthracene in dust deposition, a polycyclic aromatic hydrocarbon with carcinogenic properties.",
            "Cd(dust_deposition)": "Cadmium in dust deposition, a toxic metal causing kidney damage and other health issues.",
        }

        if not df_indicator["name"].isin(description_mapping.keys()).all():
            raise ValueError(
                "Some indicator names do not have a corresponding description mapping."
            )

        context.log.info(
            f"The description mapping for 'indicator' DataFrame is:\n{description_mapping}"
        )

        df_indicator["description"] = df_indicator["name"].map(description_mapping)

        context.log.info("The added 'description' column.")

        context.log.info(
            f"Added description first 10 rows:\n{df_indicator['description'].head(10)}"
        )

        df_indicator = drop_rows_with_nulls(df_indicator, Indicator)

        df_indicator = df_indicator.sort_values("name")

        context.log.info(
            f"'indicator' DataFrame created successfully.\n{df_indicator.head(3)}"
        )

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            data_frame=df_indicator,
            asset_key="create_dataframe_indicator",
            description="Indicator DataFrame created",
        )

        return df_indicator

    except Exception as e:

        raise Failure(f"Failed to create 'indicator' DataFrame: {e}") from e


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.TIME_AVERAGING_TABLE,
        ),
    },
)
def create_dataframe_time_averaging(
    context: AssetExecutionContext,
    rename_columns_and_values_air_quality_annual_statistics_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Creates 'time_averaging' DataFrame from the sanitized
    'air quality annual statistics' data.
    """
    try:
        df_source = rename_columns_and_values_air_quality_annual_statistics_data

        log_dataframe_info(context, df_source, "Data source")

        df_time_averaging = df_source[
            ["time_averaging", "minutes", "hours", "days"]
        ].drop_duplicates()

        df_time_averaging = drop_rows_with_nulls(df_time_averaging, TimeAveraging)

        context.log.info(
            f"'time_averaging' DataFrame created successfully.\n{df_time_averaging.head(3)}"
        )

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            data_frame=df_time_averaging,
            asset_key="create_dataframe_time_averaging",
            description="TimeAveraging DataFrame created",
        )

        return df_time_averaging

    except Exception as e:

        raise Failure(f"Failed to create 'time_averaging' DataFrame: {e}") from e


@asset(
    group_name=AnnualStatisticsGroups.DATA_PROCESSING,
    metadata={
        "categories": get_metadata_categories(
            Categories.AIR_QUALITY,
            Categories.DATA_PROCESSING,
            Categories.ANNUAL_STATISTICS_DATA,
            Categories.MEASUREMENT_TABLE,
            Categories.MEASUREMENT_ANNUAL_TABLE,
        ),
    },
)
def create_dataframe_measurement(
    context: AssetExecutionContext,
    rename_columns_and_values_air_quality_annual_statistics_data: pd.DataFrame,
) -> pd.DataFrame:
    """Creates 'measurement' DataFrame from the sanitized 'air quality annual statistics' data."""
    try:
        df_source = rename_columns_and_values_air_quality_annual_statistics_data

        log_dataframe_info(context, df_source, "Data source")

        # Extract all the necessary columns
        measurement_columns = [
            # Identifiers and metadata
            "id_measurement",
            "year",
            "station_code",
            "zone_code",
            "indicator_type",
            # Time averaging information
            "time_averaging",
            # Measurement counts and completeness
            "number_of_measurements",
            "valid_measurements_count",
            "completeness_%",
            # General measurement statistics (averages, minimums, maximums)
            "avg_µg_m3",
            "min_µg_m3",
            "max_µg_m3",
            "avg_mg_m3",
            "min_mg_m3",
            "max_mg_m3",
            "avg_µg_m2_day",
            "min_µg_m2_day",
            "max_µg_m2_day",
            "avg_ng_m3",
            "min_ng_m3",
            "max_ng_m3",
            # Exceedances and percentiles for S1
            "s1_exceedances_200",
            "s1_exceedances_350",
            "s1_19th_max_µg_m3",
            "s1_25th_max_µg_m3",
            "s1_percentile_99_7_µg_m3",
            "s1_percentile_99_8_µg_m3",
            # Exceedances and percentiles for S24
            "s24_exceedances_50",
            "s24_exceedances_125",
            "s24_4th_max_µg_m3",
            "s24_36th_max_µg_m3",
            "s24_max_µg_m3",
            "s24_percentile_90_4_µg_m3",
            "s24_percentile_99_2_µg_m3",
            # Exceedances and percentiles for S8max
            "s8max_max_mg_m3",
            "s8max_max_26th_µg_m3",
            "s8max_percentile_93_2_µg_m3",
            "s8max_days_above_120",
            # Seasonal averages and completeness
            "winter_avg_µg_m3",
            "winter_completeness_%",
            "summer_completeness_%",
            "summer_complete_months_count_april_september",
            "summer_winter_count",
            "summer_winter",
            # Other measurements and indices
            "aot40_may_july_µg_m3_h",
            "somo35_µg_m3_d",
        ]

        df_measurement = df_source[measurement_columns]

        # Replace Greek 'µ' with micro character
        context.log.info("Replacing Greek 'µ' with micro character 'μ'.")
        df_measurement.columns = df_measurement.columns.map(
            replace_greek_mu_with_micro_character
        )

        context.log.warning(
            (
                "The replacement of Greek 'µ' with micro character 'μ'"
                "is important for the development of the data model.\n"
                "The text editor may not display the micro character correctly"
                "or even find it correctly."
                "They are different characters,"
                "so be careful when copying and pasting the code."
            )
        )

        df_measurement = drop_rows_with_nulls(df_measurement, Measurement)

        df_measurement = df_measurement.sort_values(by="id_measurement")

        context.log.info(
            f"Columns in 'measurement' DataFrame:\n{df_measurement.columns}"
        )

        # Change dtype columns matching the model
        df_measurement = change_dataframe_column_types(
            df_measurement, Measurement, context
        )

        context.log.info(
            (
                f"'measurement' DataFrame created successfully.\n{df_measurement.head(3)}"
                f"dtype: {df_measurement.dtypes}"
            )
        )

        # Log AssetMaterialization with additional metadata
        log_asset_materialization(
            context=context,
            data_frame=df_measurement,
            asset_key="create_dataframe_measurement",
            description="Measurement DataFrame created",
        )

        return df_measurement

    except Exception as e:

        raise Failure(f"Failed to create 'measurement' DataFrame: {e}") from e


def prepare_dataframe(
    context: AssetExecutionContext,
    df_source: pd.DataFrame,
    columns: List[str],
    model_class: Type[DeclarativeMeta],
    df_name: str,
    sort_by: List[str] = None,
) -> pd.DataFrame:
    """Prepares a DataFrame by extracting columns, dropping duplicates and nulls, sorting, and reordering."""

    # Extract relevant columns
    df = df_source[columns].drop_duplicates()

    # Drop rows with nulls based on the model
    df = drop_rows_with_nulls(df, model_class)

    # Apply default ordering if specified
    if sort_by:
        df = df.sort_values(by=sort_by)
    else:
        df = apply_default_ordering(df, model_class, context)

    # Reorder DataFrame columns to match model columns
    model_columns = get_model_non_primary_keys_and_non_generated_columns(model_class)
    df = df[model_columns]

    context.log.info(f"'{df_name}' DataFrame created successfully.")
    log_dataframe_info(context, df, df_name)

    return df

"""
Helper functions for extracting records from the 'air quality annual statistics' data.
"""

# Python
import math
import random

# Third-party
import pandas as pd
from pandas import json_normalize
import numpy as np

# Dagster
from dagster import (
    AssetExecutionContext,
)


def extract_records(context: AssetExecutionContext, df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts records from the 'air quality annual statistics' data DataFrame.
    """

    context.log.info("Extracting records from the 'air quality annual statistics' data")
    data_column = "Lista statystyk"  # Polish for 'Statistics list'
    records_series = df[data_column]

    # Start flattening and normalizing
    context.log.info("➡️ Flattening the list of statistics and normalizing data")
    all_records = [item for sublist in records_series for item in sublist]
    df_records = json_normalize(all_records)

    # Data preview
    context.log.info("➡️ Previewing extracted records")
    context.log.info(f"Columns: {df_records.columns}")
    context.log.info(f"Types: {df_records.dtypes}")
    context.log.info(f"3 first rows: {df_records.head(3)}")

    # Random row preview
    context.log.info("➡️ Previewing a random record from the extracted data")
    random_index = random.randint(0, len(df_records))
    context.log.info(df_records.iloc[random_index])

    # Check for duplicates
    context.log.info("➡️ Checking for duplicate records in the data")
    duplicates = df_records.duplicated().sum()

    if duplicates == 0:
        context.log.info("There are no duplicates")
    else:
        context.log.info(f"Number of duplicates: {duplicates}")

        df_records.drop_duplicates(inplace=True)

        context.log.info(f"Duplicates dropped: {duplicates}")

    # Checking non-null columns
    context.log.info("➡️ Identifying columns with no null values")
    non_null_columns = df_records.columns[df_records.notnull().all()].tolist()
    context.log.info(f"Non-null columns:\n{non_null_columns}")

    # Check id values
    context.log.info("➡️ Checking for unique IDs in the data")

    id_column = df_records["id"]
    unique_ids = id_column.unique()
    unique_ids_equal_length_diff = len(df_records) - len(unique_ids)

    if unique_ids_equal_length_diff == 0:
        context.log.info("All ids are unique")
    else:
        context.log.info(
            (
                "Number of ids that are not unique:\n"
                f"unique_id: {unique_ids_equal_length_diff}\n"
                f"total_records: {len(df_records)}\n"
                f"the difference: {unique_ids_equal_length_diff}"
            )
        )

    # Check 'Year' values
    context.log.info("➡️ Analyzing the distribution of years in the data")
    year_column = df_records["Rok"]
    unique_years = year_column.value_counts().sort_index()

    context.log.info(f"Unique years (first 100):\n{unique_years[:100]}")
    context.log.info(f"Number of unique years: {len(unique_years)}")
    unique_ids_x_unique_years = len(unique_ids) * len(unique_years)
    context.log.info(
        (
            f"Unique ids x unique years: {unique_ids_x_unique_years}\n"
            f"Total records: {len(df_records)}"
        )
    )

    # Station code analysis
    context.log.info("➡️ Analyzing unique station codes in the data")
    station_code_column = df_records["Kod stacji"]  # Polish for 'Station code'
    unique_station_codes = station_code_column.unique()

    context.log.info(f"Unique station codes [first 20]:\n{unique_station_codes[:20]}")
    context.log.info(f"Number of unique station codes: {len(unique_station_codes)}")

    # Voivodeship analysis
    context.log.info("➡️ Analyzing unique voivodeships areas in the data")
    voivodeship_column = df_records[["Województwo", "Nazwa strefy"]]

    unique_areas = voivodeship_column.drop_duplicates()

    context.log.info(f"Unique voivodeships areas (first 100):\n{unique_areas[:100]}")
    context.log.info(f"Number of unique voivodeships areas: {len(unique_areas)}")

    unique_voivodeships = voivodeship_column["Województwo"].unique()
    context.log.info(f"Unique voivodeships (first 100):\n{unique_voivodeships[:100]}")
    context.log.info(f"Number of unique voivodeships: {len(unique_voivodeships)}")

    unique_zone_names = voivodeship_column["Nazwa strefy"].unique()

    # compare the length of the unique unique_areas and the unique zone_names

    unique_areas_unique_zone_names_comparison = (
        f"unique_areas: {len(unique_areas)}\n"
        f"unique_zone_names: {len(unique_zone_names)}\n"
    )
    if len(unique_areas) == len(unique_zone_names):
        context.log.info(
            (
                "The number of unique areas and zone names are equal:\n"
                f"{unique_areas_unique_zone_names_comparison}"
            )
        )

    else:
        context.log.info(
            (
                "The number of unique areas and zone names are not equal"
                f"{unique_areas_unique_zone_names_comparison}"
            )
        )

    # Indicator type analysis
    context.log.info("➡️ Analyzing indicator types in the data")
    indicator_types_column = df_records["Wskaźnik"]  # Polish for 'Indicator type'

    code_stations_column = df_records["Kod stacji"]
    unique_code_stations = code_stations_column.unique()

    context.log.info(f"Unique code stations (first 100):\n{unique_code_stations[:100]}")
    context.log.info(f"Number of unique code stations: {len(unique_code_stations)}")

    empty_indicator_types = indicator_types_column.isnull().sum()
    context.log.info(f"Number of empty indicator types: {empty_indicator_types}")

    unique_indicator_types = indicator_types_column.unique()

    context.log.info(
        f"Unique indicator types (first 100):\n{unique_indicator_types[:100]}"
    )
    context.log.info(
        """
    `cdepoz` refers to chemical substances 
    measured in their deposition form, 
    which means how they settle out of the air 
    and accumulate on surfaces like 
    soil, water, or plants. 
    This is important for understanding how pollutants like 
    heavy metals and organic compounds move from the air 
    into the environment and potentially affect ecosystems 
    and human health.
        """
    )
    context.log.info(f"Number of unique indicator types: {len(unique_indicator_types)}")

    # Handling NaN values
    context.log.info("➡️ Checking for records without any NaN values")

    df_no_nan = df_records.dropna()
    non_nan_records_len = len(df_no_nan)

    if non_nan_records_len == 0:

        context.log.info("There are no records without NaN values")
    else:

        context.log.info(f"Number of records without NaN values: {len(df_no_nan)}")

        random_index = random.randint(0, non_nan_records_len)

        context.log.info(f"Record without NaN values:\n{df_no_nan.iloc[random_index]}")

    # 'Time averaging' analysis
    context.log.info("➡️ Analyzing 'Time averaging' column")

    time_averaging_column = df_records["Czas uśredniania"]
    time_averaging_stats = time_averaging_column.value_counts()

    context.log.info(f"Time averaging stats:\n{time_averaging_stats}")

    # Summer/Winter analysis
    context.log.info("➡️ Analyzing 'Summer/Winter' columns")

    summer_winter_summer_column = df_records["Lato/Zima"]
    summer_winter_summer_number = df_records["Liczba Lato/Zima"]

    summer_winter_summer_stats = summer_winter_summer_column.value_counts()
    summer_winter_summer_min_max = (
        summer_winter_summer_number.min(),
        summer_winter_summer_number.max(),
    )
    summer_winter_summer_number_stats = summer_winter_summer_number.value_counts()
    summer_winter_summer_number_min_max = (
        summer_winter_summer_number.min(),
        summer_winter_summer_number.max(),
    )

    context.log.info(f"Summer/Winter stats:\n{summer_winter_summer_stats}")
    context.log.info(f"Summer/Winter number min/max:\n{summer_winter_summer_min_max}")

    context.log.info(
        f"Summer/Winter number stats:\n{summer_winter_summer_number_stats}"
    )
    context.log.info(
        f"Summer/Winter number min/max:\n{summer_winter_summer_number_min_max}"
    )

    return df_records


def check_candidates_for_integers(context: AssetExecutionContext, df: pd.DataFrame):
    """Check if the columns that are candidates for integers are indeed integers."""

    context.log.info("➡️ Checking the columns for candidates that could be integers")

    candidates_for_integers = [
        "Liczba pomiarów",
        "Liczba ważnych pom.",
        "L>200 (S1)",
        "L>350 (S1)",
        "L>50 (S24)",
        "L>125 (S24)",
        "L. dni > 120 (S8max)",
        "Liczba kompletnych mies. letnich (IV-IX)",
        "Liczba Lato/Zima",
        "Lato/Zima",
    ]

    for column in candidates_for_integers:

        context.log.info(f"➡️ Checking column: {column}")
        context.log.info(f"Basic statistics:\n{df[column].describe()}")
        context.log.info(f"Median: {df[column].median()}")
        context.log.info(f"Mode: {df[column].mode()}")

        # Check if the column is a natural number
        if are_all_natural_numbers(df[column], context):
            context.log.info(f"✅ Column values '{column}' are natural numbers!")
        else:
            context.log.warning(
                f"❌ Column values '{column}' are not natural numbers :("
            )


def are_all_natural_numbers(iterable, context):
    """
    Check if all values in an iterable are natural numbers.
    Log the first 100 unique non-natural numbers in ascending order if not all numbers are natural.
    """

    non_natural_numbers = sorted(
        {
            value
            for value in iterable
            if value is not None
            and not math.isnan(value)
            and not is_natural_number(value)
        }
    )

    if non_natural_numbers:
        context.log.warning(
            f"Found non-natural numbers (first 100, sorted): {non_natural_numbers[:100]}"
        )
        return False
    return True


def is_natural_number(value):
    """
    Check if a single value is a natural number (positive integer including zero).
    """
    # Check if the value is a whole number and non-negative
    return (
        isinstance(value, (int, float, np.number))
        and value >= 0
        and value == int(value)
    )

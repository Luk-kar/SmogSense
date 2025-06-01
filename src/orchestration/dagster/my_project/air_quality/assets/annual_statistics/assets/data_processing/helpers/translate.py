"""
This module contains helper functions for translating column names and values
from Polish to English.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
)


def translate_time_averaging_column(
    context: AssetExecutionContext, data: pd.DataFrame
) -> pd.DataFrame:
    """Translates 'Time averaging' column with tis values from Polish to English."""

    context.log.info("➡️ Translating 'Time averaging' column name and values")

    translated_data = data.copy()

    context.log.info("➡️ Translating 'Time averaging' column name")

    # translate 'Time averaging' column from Polish to English
    translated_data["Time averaging"] = translated_data["Czas uśredniania"]

    translated_data.drop(columns=["Czas uśredniania"], inplace=True)

    context.log.info(
        f"Columns after dropping 'Czas uśredniania':\n{translated_data.columns}"
    )

    context.log.info("➡️ Translating 'Time averaging' column values")

    context.log.info(
        f"Original 'Time averaging' values:\n{translated_data['Time averaging'].unique()}"
    )

    # translate 'Time averaging' values from Polish to English
    translated_data["Time averaging"] = translated_data["Time averaging"].apply(
        translate_time_averaging_value
    )

    context.log.info(
        f"Translated 'Time averaging' values:\n{translated_data['Time averaging'].unique()}"
    )

    return translated_data


def translate_time_averaging_value(value: str) -> str:
    """Translates 'Time averaging' values from Polish to English."""

    # Define mappings for suffix translation
    translation = {
        "1m": "1 minute",
        "1g": "1 hour",
        "24g": "1 day",
        "1t": "1 week",
        "2t": "2 weeks",
    }

    try:
        # Look up the value in the translation dictionary
        if value in translation:

            translated = translation[value]

            return translated
        else:
            # Log and return the original value if it cannot be translated
            raise ValueError(
                (
                    f"Value '{value}' is not in the translation dictionary,\n"
                    "'translation':"
                    f"\n{translation}"
                )
            )
    except Exception as e:
        raise BaseException(f"Error while translating value '{value}': {e}") from e


def translate_zone_name_and_extract_zone_type(
    context: AssetExecutionContext, data: pd.DataFrame
) -> pd.DataFrame:
    """
    Translates 'zone_name' column with its values
    from Polish to English and extracts the 'zone_type'.
    """

    # Translate 'zone_name' column name and values
    context.log.info("➡️ Translating 'zone_name' column name and values")

    translated_data = data.copy()

    context.log.info("➡️ Translating 'zone_name' column name")

    translated_data["zone_name"] = translated_data["Nazwa strefy"]
    translated_data.drop(columns=["Nazwa strefy"], inplace=True)

    context.log.info(
        f"Columns after dropping 'Nazwa strefy':\n{translated_data.columns}"
    )

    # Extract 'zone_type' from 'zone_name' to a new column

    extract_and_translate_zone_type(context, translated_data)

    return translated_data


def extract_and_translate_zone_type(
    context: AssetExecutionContext, translated_data: pd.DataFrame
) -> pd.DataFrame:
    """Extracts 'zone_type' from 'zone_name' values and translates them from Polish to English."""

    translation_zone_type = {
        "strefa": "zone",
        "Aglomeracja": "agglomeration",
        "miasto": "city",
    }

    context.log.info("➡️ Extracting 'zone_type' from 'zone_name'")

    translated_data["zone_type"] = translated_data["zone_name"].apply(
        lambda field: extract_zone_type(field, list(translation_zone_type.keys()))
    )

    context.log.info(f"Columns after adding 'zone_type':\n{translated_data.columns}")

    # remove the 'zone_type' from the 'zone_name'
    context.log.info("➡️ Removing 'zone_type' from 'zone_name' column values")
    translated_data["zone_name"] = translated_data["zone_name"].apply(
        lambda field: remove_zone_type(field, list(translation_zone_type.keys()))
    )

    context.log.info(
        (
            "Values of 'zone_name' after removing 'zone_type' (first 100):\n"
            f"{translated_data['zone_name'].unique()[:100]}"
        )
    )

    # translate the 'zone_type'/'Typ strefy' values
    context.log.info("➡️ Translating 'zone_type' column values")

    context.log.info(
        f"Original 'zone_type' values (first 100):\n{translated_data['zone_type'].unique()[:100]}"
    )

    translated_data["zone_type"] = translated_data["zone_type"].apply(
        lambda field: translate_zone_type_value(field, translation_zone_type)
    )

    context.log.info(
        (
            "Translated 'zone_type'/'Typ strefy' values (first 100):\n"
            f"{translated_data['zone_type'].unique()[:100]}"
        )
    )


def extract_zone_type(value: str, zone_types: list) -> str:
    """Extracts 'zone_type' from 'zone_name' values."""

    try:
        # Check if the value contains any of the zone_types
        for zone_type in zone_types:
            if zone_type.lower() in value.lower():
                return zone_type

        raise ValueError(
            (
                f"\nValue '{value}' does not contain any of the zone_types,\n"
                f"zone_types: {zone_types}"
            )
        )

    except Exception as e:
        raise BaseException(
            f"Error while extracting zone_type from value '{value}': {e}"
        ) from e


def remove_zone_type(value: str, zone_types: list[str]) -> str:
    """Removes 'zone_type' from 'zone_name' values."""

    try:
        # Check if the value contains any of the zone_types
        for zone_type in zone_types:
            if zone_type.lower() in value.lower():
                return (
                    value.replace(zone_type, "").replace(zone_type.lower(), "").strip()
                )

        raise ValueError(
            (
                f"Value '{value}' does not contain any of the zone_types,\n"
                f"zone_types: {zone_types}"
            )
        )

    except Exception as e:
        raise BaseException(
            f"Error while removing zone type from value '{value}': {e}"
        ) from e


def translate_zone_type_value(value: str, translation: dict[str, str]) -> str:
    """Translates 'zone_type'/'Typ strefy' values from Polish to English."""

    try:
        # Look up the value in the translation dictionary
        if value in translation:

            translated = translation[value].strip()

            return translated
        else:
            # Log and return the original value if it cannot be translated
            raise ValueError(
                (
                    f"Value '{value}' is not in the translation dictionary,\n"
                    "'translation':"
                    f"\n{translation}"
                )
            )
    except Exception as e:
        raise BaseException(f"Error while translating value '{value}': {e}") from e


def translate_indicator_type_column(
    context: AssetExecutionContext, data_input: pd.DataFrame
) -> pd.DataFrame:
    """Translates 'Indicator type' column with its values from Polish to English."""

    context.log.info("➡️ Translating 'Indicator type' column name and values")

    translated_data = data_input.copy()

    context.log.info("➡️ Translating 'Indicator type' column name")

    translated_data["Indicator type"] = translated_data["Wskaźnik"]

    translated_data.drop(columns=["Wskaźnik"], inplace=True)

    context.log.info(f"Columns after dropping 'Wskaźnik':\n{translated_data.columns}")

    context.log.info("➡️ Translating 'Indicator type' column values")

    context.log.info(
        f"Original 'Indicator type' values:\n{translated_data['Indicator type'].unique()}"
    )

    # translate 'Indicator type' values from Polish to English
    translated_data["Indicator type"] = translated_data["Indicator type"].apply(
        translate_indicator_type_value
    )

    context.log.info(
        f"Translated 'Indicator type' values:\n{translated_data['Indicator type'].unique()}"
    )

    return translated_data


def translate_indicator_type_value(value: str) -> str:
    """Translates 'Indicator type' values from Polish to English."""

    # Define mappings for translation
    translation = {
        "(cdepoz)": "(dust_deposition)",
        "formaldehyd": "formaldehyde",
    }

    missing_keys = [key for key in translation if key not in value]

    try:

        if any(missing_keys):

            for to_translate, translated_term in translation.items():
                if to_translate in value:
                    translated = value.replace(to_translate, translated_term)
                    return translated

        return value

    except Exception as e:
        raise BaseException(f"Error while translating value '{value}': {e}") from e


def translate_column_names(
    context: AssetExecutionContext, data_source: pd.DataFrame
) -> pd.DataFrame:
    """Translates column names from Polish to English."""

    context.log.info("➡️ Translating column names from Polish to English")

    data = data_source.copy()

    context.log.info("➡️ Checking if one column is a duplicate of another")

    result = check_duplicate_columns(data, "Max [µg/m3]", "Maks [µg/m3]")

    context.log.info(f"Duplicate columns check result:\n{result}")

    # Dropping corrupted columns
    context.log.info("➡️ Dropping corrupted columns: 'Max [µg/m3]', 'Maks [µg/m3]'")

    data.drop(columns=["Max [µg/m3]", "Maks [µg/m3]"], inplace=True)

    context.log.info(f"After dropping corrupted columns:\n{data.columns}")

    # Translation dictionary
    context.log.info("➡️ Recreating the 'Max [µg/m3]' based on 'Maks [ng/m3]' column")

    data["Max [µg/m3]"] = data["Maks [ng/m3]"] / 1000

    translation = {
        # Identifiers and metadata
        "id": "id_measurement",
        "Rok": "year",
        "Województwo": "province",
        "Kod strefy": "zone_code",
        "zone_name": "zone_name",
        "zone_type": "zone_type",
        "Kod stacji": "station_code",
        "Indicator type": "indicator_type",
        # Time averaging information
        "Time averaging": "time_averaging",
        "minutes": "minutes",
        "hours": "hours",
        "days": "days",
        # Measurement counts and completeness
        "Liczba pomiarów": "number_of_measurements",
        "Liczba ważnych pom.": "valid_measurements_count",
        "Kompletność [%]": "completeness_%",
        # General measurement statistics (averages, minimums, maximums)
        "Średnia [µg/m3]": "avg_µg_m3",
        "Min [µg/m3]": "min_µg_m3",
        "Max [µg/m3]": "max_µg_m3",
        "Średnia [mg/m3]": "avg_mg_m3",
        "Min [mg/m3]": "min_mg_m3",
        "Maks [mg/m3]": "max_mg_m3",
        # Measurements in other units
        "Średnia [ng/m3]": "avg_ng_m3",
        "Min [ng/m3]": "min_ng_m3",
        "Maks [ng/m3]": "max_ng_m3",
        "Średnia [µg/m2/dzień]": "avg_µg_m2_day",
        "Min [µg/m2/dzień]": "min_µg_m2_day",
        "Maks [µg/m2/dzień]": "max_µg_m2_day",
        # Exceedances and percentiles for S1
        "L>200 (S1)": "s1_exceedances_200",
        "L>350 (S1)": "s1_exceedances_350",
        "19 maks. (S1) [µg/m3]": "s1_19th_max_µg_m3",
        "25 maks. (S1) [µg/m3]": "s1_25th_max_µg_m3",
        "Perc. 99.7 (S1) [µg/m3]": "s1_percentile_99_7_µg_m3",
        "Perc. 99.8 (S1) [µg/m3]": "s1_percentile_99_8_µg_m3",
        # Exceedances and percentiles for S24
        "L>50 (S24)": "s24_exceedances_50",
        "L>125 (S24)": "s24_exceedances_125",
        "4 maks. (S24) [µg/m3]": "s24_4th_max_µg_m3",
        "36 maks. (S24) [µg/m3]": "s24_36th_max_µg_m3",
        "Maks (S24) [µg/m3]": "s24_max_µg_m3",
        "Perc. 90.4 (S24) [µg/m3]": "s24_percentile_90_4_µg_m3",
        "Perc. 99.2 (S24) [µg/m3]": "s24_percentile_99_2_µg_m3",
        # Exceedances and percentiles for S8max
        "Maks (S8max) [mg/m3]": "s8max_max_mg_m3",
        "26 maks (S8max) [µg/m3]": "s8max_max_26th_µg_m3",
        "Per. S93.2 (S8max) [µg/m3]": "s8max_percentile_93_2_µg_m3",
        "L. dni > 120 (S8max)": "s8max_days_above_120",
        # Seasonal averages and completeness
        "Śr. zimowa [µg/m3]": "winter_avg_µg_m3",
        "Kompl. lato [%]": "summer_completeness_%",
        "Kompl. zima [%]": "winter_completeness_%",
        "Liczba kompletnych mies. letnich (IV-IX)": "summer_complete_months_count_april_september",
        "Liczba Lato/Zima": "summer_winter_count",
        "Lato/Zima": "summer_winter",
        # Other measurements and indices
        "AOT40 V-VII [µg/m3]*h": "aot40_may_july_µg_m3_h",
        "SOMO35 [µg/m3]*d": "somo35_µg_m3_d",
    }

    missing_keys = [key for key in translation if key not in data.columns]

    # check if all keys are in the column names
    if not all(missing_keys):
        raise ValueError(
            (
                "Not all keys are in the column names,\n"
                f"keys: {translation.keys()}\n"
                f"columns: {data.columns}"
                f"missing keys: {missing_keys}"
            )
        )

    context.log.info(f"Current columns names:\n{data.columns}")

    context.log.info("➡️ Translating column names")

    data.rename(columns=translation, inplace=True)

    context.log.info(f"Columns after translation:\n{data.columns}")

    context.log.info("➡️ Rearranging the columns")

    ordered_columns = list(translation.values())

    data = data[ordered_columns]

    context.log.info(f"Columns after rearranging:\n{data.columns}")

    return data


def check_duplicate_columns(data: pd.DataFrame, col1: str, col2: str):
    """
    Checks if two columns are duplicates based on the given conditions:
    1. When one column is NaN/None, the other has a value and vice versa.
    2. Both columns are NaN/None simultaneously.
    3. Both columns have the same value at the same time.

    Parameters:
        data (pd.DataFrame): The DataFrame to check.
        col1 (str): The name of the first column.
        col2 (str): The name of the second column.

    Returns:
        dict: A dictionary with the counts of each condition.
    """
    # Ensure the columns exist
    if col1 not in data.columns or col2 not in data.columns:
        raise ValueError(
            f"One or both columns '{col1}' and '{col2}' are missing in the DataFrame."
        )

    # Conditions
    condition_1 = ((data[col1].isna()) & (data[col2].notna())) | (
        (data[col1].notna()) & (data[col2].isna())
    )
    condition_2 = (data[col1].isna()) & (data[col2].isna())
    condition_3 = (data[col1] == data[col2]) & (data[col1].notna())
    non_condition = (
        (data[col1] != data[col2]) & (data[col1].notna()) & (data[col2].notna())
    )

    # Counts of each condition
    result = {
        "col1_is_nan_col2_has_value_or_vice_versa": condition_1.sum(),
        "both_are_nan": condition_2.sum(),
        "both_have_same_value": condition_3.sum(),
        "non_duplicate_values": non_condition.sum(),
    }

    return result

"""
Reusable utility functions for translating pollutant names and indicator types.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
)


def translate_pollutant_name(pollutant_name: str) -> str:
    """
    Translates the pollutant name to a more readable format.
    """

    translations_pollutants = {
        "O3_3letnia": "O3_avg_3_yearly",
        "PM25_sr_roczna": "PM25_avg_yearly",
        "NO2_sr_roczna": "NO2_avg_yearly",
    }

    return translations_pollutants.get(pollutant_name, pollutant_name)


def translate_pollutant_names(
    context: AssetExecutionContext, df_geometry: pd.DataFrame
) -> pd.DataFrame:
    """
    Translates the pollutant names in the geometry dataframe.
    """

    context.log.info("➡️ Translating 'pollutant names'...")

    df_geometry["pollutant_name"] = df_geometry["pollutant_name"].apply(
        translate_pollutant_name
    )

    context.log.info(
        "Unique 'pollutants names' after translation:\n"
        f"{df_geometry['pollutant_name'].unique()}"
    )

    return df_geometry


def translate_indicator_type(indicator_type) -> str:
    """
    Translates the indicator type to a more readable format.
    """

    translations_indicators = {
        "OZ": "Health",
        "OR": "Agriculture",
    }

    return translations_indicators.get(indicator_type, indicator_type)


def translate_column(
    context: AssetExecutionContext,
    df: pd.DataFrame,
    column: str,
    translation_func,
    label: str,
) -> pd.DataFrame:
    """
    Translates the values in the given column using the provided translation function.
    """

    context.log.info(f"➡️ Translating {label}...")
    before = df[column].unique()
    df[column] = df[column].apply(translation_func)
    after = df[column].unique()
    context.log.info(f"Before translation: {before}\nAfter translation: {after}")
    return df

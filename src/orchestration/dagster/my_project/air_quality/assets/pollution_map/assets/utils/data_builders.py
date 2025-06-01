"""
Contains utility functions to build dataframes from the given data.
"""

# Third-party
import pandas as pd

# Pipeline
# fmt: off
from air_quality.assets.\
pollution_map.assets.utils.json_extractor import (
    get_indicator_type,
    get_date_published,
)
# fmt: on


def build_dataframe_from_pollutants(data: dict, row_builder_func) -> pd.DataFrame:
    """
    Builds a dataframe from the given data using the provided row builder function.
    """

    rows = []
    for pollutant_name, characteristics in iterate_pollutants(data):
        rows.extend(row_builder_func(pollutant_name, characteristics))
    return pd.DataFrame(rows)


def build_pollutant_rows(pollutant_name: str, characteristics: dict) -> list:
    """
    Builds pollutant rows from the given pollutant name and characteristics.
    """

    indicator_type = get_indicator_type(characteristics)
    return [{"pollutant_name": pollutant_name, "indicator_type": indicator_type}]


def build_measurement_rows(pollutant_name: str, characteristics: dict) -> list:
    """
    Builds measurement rows from the given pollutant name and characteristics.
    """

    data_year = characteristics.get("year")

    if not data_year or not isinstance(data_year, int):
        raise ValueError(f"❌ Could not extract year from indicator:\n{pollutant_name}")

    date_published = get_date_published(characteristics)

    return [
        {
            "pollutant_name": pollutant_name,
            "data_year": data_year,
            "date_published": date_published,
        }
    ]


def iterate_pollutants(data: dict):
    """
    Common iterator to extract pollutant_name and characteristics from the data.
    """
    for indicator_name, characteristics in data.items():
        pollutant_name = indicator_name
        if not pollutant_name:
            raise ValueError(
                f"❌ Could not extract pollutant name from indicator:\n{indicator_name}"
            )
        yield pollutant_name, characteristics

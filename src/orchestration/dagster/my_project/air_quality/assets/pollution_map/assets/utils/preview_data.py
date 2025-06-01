"""
Contains assets for uploading and downloading 'air quality sensor' data to and from MinIO.
"""

# Python
from typing import Any

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetExecutionContext,
)

# Pipeline
from common.utils.dataframe import (
    convert_to_dataframe,
)
from common.utils.logging import (
    log_dataframe_info,
)
from common.utils.validation import (
    log_data_type_and_validate_if_list_or_dict,
)


def preview_air_quality_map_pollutant_data(
    context: AssetExecutionContext,
    download_air_quality_map_pollutant_data_from_minio: Any,  # Union[list, dict]
) -> pd.DataFrame:
    """
    Preview the air quality sensor data for the 'pollution map' asset.
    """

    data = download_air_quality_map_pollutant_data_from_minio

    log_data_type_and_validate_if_list_or_dict(context, data)

    df = convert_to_dataframe(context, data)

    log_dataframe_info(context, df, "Air quality map pollutant data")

    unique_keys = get_unique_keys(data)

    context.log.info(f"Unique keys: {unique_keys}")

    unique_nazwa_wska, unique_typ_wskaz = extract_unique_air_quality_indicators(data)

    context.log.info(
        (
            "➡️ Extracting unique air quality indicators..."
            f"• Unique 'nazwa_wska' values (first 50): {unique_nazwa_wska}"
            f"• Unique 'typ_wskaz' values (first 50): {unique_typ_wskaz}"
        )
    )

    date_published, keywords = get_unique_metadata(data)

    ids = extract_ids_by_indicator(data)

    context.log.info(
        (
            "➡️ Extracting unique metadata..."
            f"• Unique 'schema:datePublished' values (first 50): {date_published}"
            f"• Unique 'schema:keywords' values (first 50): {keywords}"
            f"• Unique '@id' values (first 50): {ids}"
        )
    )


def get_unique_keys(data: Any, parent_key: str = "") -> set:
    """
    Recursively collects unique keys from a nested structure.
    """

    keys = set()

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            keys.add(full_key)
            keys.update(get_unique_keys(value, full_key))
    elif isinstance(data, list):
        for item in data:
            keys.update(get_unique_keys(item, parent_key))

    return keys


def extract_unique_air_quality_indicators(flattened_data: dict) -> tuple:
    """
    Extracts unique values for 'nazwa_wska' and 'typ_wskaz' from the dataset.
    """

    unique_nazwa_wska = set()
    unique_typ_wskaz = set()

    for pollutant_data in flattened_data.values():
        n_wska = extract_unique_values(
            pollutant_data, ["indicator", "features", "properties", "nazwa_wska"]
        )
        t_wskaz = extract_unique_values(
            pollutant_data, ["indicator", "features", "properties", "typ_wskaz"]
        )

        unique_nazwa_wska.update(n_wska)
        unique_typ_wskaz.update(t_wskaz)

    return list(unique_nazwa_wska)[:50], list(unique_typ_wskaz)[:50]


def extract_unique_values(data: dict, path: list, limit: int = 50) -> list:
    """
    Extracts unique values from a nested data structure based on a given path.
    """

    unique_values = set()

    def recursive_extraction(data: Any, path: list):

        if not path:

            if isinstance(data, str):
                unique_values.update(data.split(", "))
            else:
                unique_values.add(data)
            return

        key = path[0]

        if isinstance(data, dict):

            if key in data:
                recursive_extraction(data[key], path[1:])

        elif isinstance(data, list):

            for item in data:
                recursive_extraction(item, path)

    recursive_extraction(data, path)

    return list(unique_values)[:limit]


def get_unique_metadata(flattened_data: dict) -> tuple:
    """
    Extracts unique values for 'schema:datePublished' and 'schema:keywords' from the dataset.
    """

    date_published = set()
    keywords = set()

    for pollutant_data in flattened_data.values():
        dp = extract_unique_values(
            pollutant_data, ["indicator", "meta", "schema:datePublished"]
        )
        kw = extract_unique_values(
            pollutant_data, ["indicator", "meta", "schema:keywords"]
        )

        date_published.update(dp)
        keywords.update(kw)

        if len(date_published) >= 50 and len(keywords) >= 50:
            break

    return list(date_published)[:50], list(keywords)[:50]


def extract_ids_by_indicator(data: dict) -> dict:
    """
    Extracts all unique '@id' values for each indicator in the dataset.

    This function processes a nested data structure and collects all values
    associated with the key '@id' for each indicator in the input dictionary.
    It ensures that the resulting list of '@id' values for each indicator is unique.
    """

    ids_by_indicator = {}

    for indicator_name, indicator_data in data.items():
        # Initialize a list to collect '@id' values for the current indicator
        collected_ids = []
        collect_ids(indicator_data, collected_ids)

        # Remove duplicates and store unique '@id' values for the indicator
        ids_by_indicator[indicator_name] = list(set(collected_ids))

    return ids_by_indicator


def collect_ids(data: Any, collected_ids: list):
    """
    Recursively collects '@id' values from a nested structure.
    """

    if isinstance(data, dict):

        for key, value in data.items():

            if key == "@id":
                collected_ids.append(value)
            else:
                collect_ids(value, collected_ids)

    elif isinstance(data, list):

        for item in data:
            collect_ids(item, collected_ids)

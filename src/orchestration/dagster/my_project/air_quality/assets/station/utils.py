"""
Contains air_quality-related utility functions.
"""

# Third-party
import pandas as pd


def normalize_city_column(city_column: pd.Series) -> pd.DataFrame:
    """
    Normalizes the 'city' column by expanding JSON-like strings into a DataFrame.

    Args:
        city_column (pd.Series): Series containing JSON-like dictionaries.

    Returns:
        pd.DataFrame: A DataFrame with normalized data.
    """

    # Apply pd.json_normalize to each dictionary to flatten the structure
    normalized_city_data = city_column.apply(pd.json_normalize)

    # Concatenate all resulting DataFrames into a single DataFrame
    concatenated_city_data = pd.concat(normalized_city_data.tolist(), ignore_index=True)

    # Rename columns
    renamed_columns_data = concatenated_city_data.rename(
        columns={
            "id": "id_area",
            "name": "city_district",
            "commune.communeName": "city",
            "commune.districtName": "county",
            "commune.provinceName": "province",
        }
    )

    return renamed_columns_data

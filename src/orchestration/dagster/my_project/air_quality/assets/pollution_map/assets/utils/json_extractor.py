"""
Contains utility functions for extracting data from JSON map.
"""

# Python
from datetime import datetime


def get_indicator_type(characteristics: dict) -> str:
    """
    Extract the first non-empty 'typ_wskaz' indicator type from 'features' inside 'indicator'.
    """
    indicators = characteristics.get("indicator", [])
    for feature in indicators:
        for f in feature.get("features", []):
            indicator_type = f.get("properties", {}).get("typ_wskaz")
            if indicator_type:
                return indicator_type
    raise ValueError("Could not extract pollutant type from given indicator data.")


def get_date_published(characteristics: dict) -> datetime:
    """
    Extract the first datePublished value from 'meta' inside 'indicator'
    and return it as a string in 'YYYY-MM-DD' format.
    """
    indicators = characteristics.get("indicator", [])
    for indicator in indicators:
        meta = indicator.get("meta", {})
        date_published_value = meta.get("schema:datePublished")
        if date_published_value:
            return datetime.strptime(date_published_value, "%d.%m.%Y").strftime(
                "%Y-%m-%d"
            )
    return None

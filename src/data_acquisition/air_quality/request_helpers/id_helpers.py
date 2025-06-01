"""
Function to fetch and extract IDs from a JSON or dict.
"""

# Python
from typing import List, Callable, Any


def fetch_ids(
    fetch_data_def: Callable[[], List[dict[str, Any]]], id_key: str = "id"
) -> List[int]:
    """
    Generic function to fetch and extract IDs from data.

    return: A list of IDs.
    """
    data = fetch_data_def()
    return [item[id_key] for sublist in data for item in sublist]

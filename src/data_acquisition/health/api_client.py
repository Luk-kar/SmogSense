"""
API client for making requests to the statistical API.

Documentation: 
https://api.stat.gov.pl/Home/BdlApi
https://bdl.stat.gov.pl/bdl/dane/podgrup/temat
"""

import requests

from src.data_acquisition.health.api_endpoints import (
    get_list_of_categories_causes_of_death_url,
    create_targeted_metric_url,
)


def fetch_data_from_url(url: str) -> dict:
    """
    Generalized function to fetch data from a given URL and return JSON response.

    Args:
        url (str): The URL to fetch data from.

    Returns:
        dict: Parsed JSON response from the API.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_categories_causes_of_death(subject_id: str) -> dict:
    """
    Retrieve categories of causes of death as JSON from the API.

    Args:
        subject_id (str): The subject ID to fetch data for like "P1344", "P1345", etc.

    Returns:
        dict: Parsed JSON response containing categories of causes of death.
    """
    print("Fetching categories causes of death...")
    url = get_list_of_categories_causes_of_death_url(subject_id)
    return fetch_data_from_url(url)


def fetch_targeted_metric(
    variable_id: str, unit_level: int = 2, page_max: int = None
) -> dict:
    """
    Retrieve targeted metric as JSON from the API.

    Args:
        variable_id (str): The variable ID to fetch data for like "6581", "1234", etc.
        unit_level (int, optional): Unit level to filter the data. Defaults to 2.

    Returns:
        dict: Parsed JSON response containing the targeted metric.
    """
    url = create_targeted_metric_url(variable_id, unit_level, page_max=page_max)
    return fetch_data_from_url(url)


def download_targeted_metrics(
    variable_ids: list, unit_level: int = 2, page_max: int = None
) -> dict:
    """
    Download a list of targeted metrics and return the data as a dictionary.

    Args:
        variable_ids (list): List of variable IDs to fetch data for.
        output_file (str): Path to save the downloaded JSON data.
        unit_level (int, optional): Unit level to filter the data. Defaults to 2.

    Returns:
        dict: Dictionary containing the targeted metrics data.
    """

    print(f"Downloading targeted metrics for {len(variable_ids)} variables...")

    metrics_data = {}

    for variable_id in variable_ids:

        try:
            metrics_data[variable_id] = fetch_targeted_metric(
                variable_id, unit_level, page_max
            )

        except requests.exceptions.RequestException as e:
            raise ValueError(
                f"Error fetching data for variable ID {variable_id}: {e}"
            ) from e

    return metrics_data

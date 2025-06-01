"""
Provides functions to fetch and process complete air quality data from the GIOS API, 
utilizing all valid arguments to retrieve all available information.
https://powietrze.gios.gov.pl/pjp/content/api
"""

# Python
from typing import List, Any

# Air quality
from src.data_acquisition.air_quality.gios_api.annual import (
    fetch_station_data,
    fetch_sensor_data,
    fetch_annual_statistics,
    fetch_map_pollutant_concentration_distribution,
)
from src.data_acquisition.air_quality.gios_api.current import (
    fetch_current_measurement_data,
    fetch_air_quality_index,
)
from src.data_acquisition.air_quality.api_endpoints import (
    ANNUAL_STATISTICS_ARGS,
    MAP_POLLUTANT_ARGS,
)

# Helpers
from src.data_acquisition.air_quality.request_helpers.fetch_requests import (
    fetch_and_process_data,
)
from src.data_acquisition.air_quality.request_helpers.id_helpers import fetch_ids


def fetch_sensor_data_all(
    sample: int = None, station_ids: List[int] = None
) -> List[Any]:
    """
    1500 requests per minute

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Stacje%20pomiarowe%20i%20stanowiska%20pomiarowe/getAutomaticAndManualSensorsUsingGET

    returns a list of all sensors for a given stations.
    """

    return fetch_and_process_data(
        fetch_ids_def=_fetch_station_ids,
        fetch_data_def=fetch_sensor_data,
        device_ids=station_ids,
        sample=sample,
    )


def fetch_current_measurement_data_all(
    sample: int = None, sensor_ids: List[int] = None
) -> List[Any]:
    """
    Fetches current measurement data for given sensors.
    """

    return fetch_and_process_data(
        fetch_ids_def=_fetch_sensor_ids,
        fetch_data_def=fetch_current_measurement_data,
        device_ids=sensor_ids,
        sample=sample,
    )


def fetch_fetch_air_quality_index_all(
    sample: int = None, station_ids: List[int] = None
) -> List[Any]:
    """
    Fetches air quality index data for given stations.
    """

    return fetch_and_process_data(
        fetch_ids_def=_fetch_station_ids,
        fetch_data_def=fetch_air_quality_index,
        device_ids=station_ids,
        sample=sample,
    )


def fetch_map_pollutants_all(
    years: List[int] = MAP_POLLUTANT_ARGS["year"],
    indicators: dict[str, dict[str, str]] = MAP_POLLUTANT_ARGS["indicator"],
) -> List[Any]:
    """
    2 requests per minute

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Mapy%20rozk%C5%82ad%C3%B3w%20st%C4%99%C5%BCe%C5%84%20zanieczyszcze%C5%84/getDistributionsOfConcentrationsMapUsingGET

    Returns a list of maps of pollutant concentration distributions.
    The data can be used to visualize the distribution of pollutant concentrations in a given year.
    """

    map_collection = []

    for year in years:
        for measure_type, value in indicators.items():
            # Convert the dictionary to a single value
            _values = value.values()

            for _value in _values:
                map_data = fetch_map_pollutant_concentration_distribution(
                    year, measure_type, _value
                )
                if map_data is not None:
                    map_collection.append(map_data)

    if not map_collection:
        raise ValueError("No data found")

    return map_collection


def fetch_annual_statistics_all(
    indicators: dict[str, str] = ANNUAL_STATISTICS_ARGS
) -> List[Any]:
    """
    2 requests per minute

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Statystyki%20roczne%20/getStatisticsUsingGET

    Returns a list of annual statistics for a given indicator
    """

    all_annual_statistics = []
    for indicator in indicators.values():
        annual_statistics = fetch_annual_statistics(indicator)
        if annual_statistics is not None:
            all_annual_statistics.extend(annual_statistics)

    return all_annual_statistics


def _fetch_station_ids() -> List[int]:
    """
    Fetches and returns a list of station IDs.
    """
    return fetch_ids(fetch_station_data)


def _fetch_sensor_ids() -> List[int]:
    """
    Fetches and returns a list of sensor IDs.
    """
    return fetch_ids(fetch_sensor_data_all)

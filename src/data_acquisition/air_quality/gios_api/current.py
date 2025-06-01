"""
air quality data from GIOS API:
https://powietrze.gios.gov.pl/pjp/content/api
https://api.gios.gov.pl/pjp-api/swagger-ui/#/

Sensors' data updated:

    hourly:
        - current measurement data
        - air quality index
        - exceedance information
"""

# Air quality
from src.data_acquisition.air_quality.request_helpers.fetch_requests import (
    fetch_all_pages,
)
from src.data_acquisition.air_quality.errors import raise_exception_with_valid_request
from src.data_acquisition.air_quality.api_endpoints import (
    API_URL,
    API_V1_URL,
    MAX_SIZE,
    GIOS_VALID_API_REQUESTS,
)


def fetch_current_measurement_data(sensor_id: int) -> list:
    """
    limit of 2 requests per minute.
    Updated each hour.

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Bie%C5%BC%C4%85ce%20dane%20pomiarowe/getDataUsingGET

    Returns a list of current measurement data for a given sensor.
    """

    _type = "data"
    command = "getData"
    size = MAX_SIZE
    url = f"{API_URL}/{_type}/{command}/{sensor_id}?size={size}"

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["current_measurement"]
        raise_exception_with_valid_request(e, url, valid_request)


def fetch_air_quality_index(station_id: int) -> list:
    """
    limit of 1500 requests per minute
    Custom update interval per sensor.

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Indeks%20jako%C5%9Bci%20powietrza/getIndexUsingGET

    Returns a list of air quality index for a given sensor.
    """

    _type = "aqindex"
    command = "getIndex"
    size = MAX_SIZE
    url = f"{API_URL}/{_type}/{command}/{station_id}?size={size}"

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["air_quality_index"]
        raise_exception_with_valid_request(e, url, valid_request)


def fetch_exceedance_information() -> list:
    """
    limit of 1500 requests per minute

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Informacje%20o%20przekroczeniu/getInformationAboutExceedingUsingGET

    Returns a list of exceedance information.
    """

    _type = "levels"
    command = "getInformationAboutExceeding"
    size = MAX_SIZE
    url = f"{API_V1_URL}/{_type}/{command}?size={size}"

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["exceedance_information"]
        raise_exception_with_valid_request(e, url, valid_request)

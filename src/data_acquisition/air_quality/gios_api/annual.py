"""
air quality data from GIOS API:
https://powietrze.gios.gov.pl/pjp/content/api
https://api.gios.gov.pl/pjp-api/swagger-ui/#/

Sensors' data updated:
    yearly:
        - measurement stations and measurement sites
        - annual statistics
        - maps of pollutant concentration distributions
"""

# Air quality
from src.data_acquisition.air_quality.request_helpers.fetch_requests import (
    fetch_all_pages,
)
from src.data_acquisition.air_quality.errors import raise_exception_with_valid_request
from src.data_acquisition.air_quality.request_helpers.url_utils import to_url_format
from src.data_acquisition.air_quality.api_endpoints import (
    API_URL,
    API_V1_URL,
    MAX_SIZE,
    GIOS_VALID_API_REQUESTS,
)
from src.data_acquisition.air_quality._types import (
    ANNUAL_STATISTICS_TYPES,
    MAP_POLLUTANT_TYPES,
)


def fetch_station_data() -> list:
    """
    limit of 2 requests per minute
    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Stacje%20pomiarowe%20i%20stanowiska%20pomiarowe/getAutomaticAndManualStationUsingGET

    Returns a list of all measurement stations.
    """

    _type = "station"
    command = "findAll"
    size = MAX_SIZE
    url = f"{API_URL}/{_type}/{command}?size={size}"

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["station_data"]
        raise_exception_with_valid_request(e, url, valid_request)


def fetch_sensor_data(station_id: int) -> list:
    """
    limit of 2 requests per minute
    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Stacje%20pomiarowe%20i%20stanowiska%20pomiarowe/getAutomaticAndManualSensorsUsingGET

    Returns a list of all sensors for a given station.
    """

    _type = "station"
    command = "sensors"
    size = MAX_SIZE
    url = f"{API_URL}/{_type}/{command}/{station_id}?size={size}"

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["sensor_data"]
        raise_exception_with_valid_request(e, url, valid_request)


## Annual statistics

INDICATOR_TYPE = ANNUAL_STATISTICS_TYPES["indicator"]


def fetch_annual_statistics(indicator: INDICATOR_TYPE) -> list:
    """
    limit of 2 requests per minute
    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Statystyki%20roczne%20/getStatisticsUsingGET

    Returns a list of annual statistics for a given indicator.
    """

    _type = "statistics"
    command = "getStatisticsForPollutants"
    size = MAX_SIZE
    formatted_indicator = to_url_format(indicator)

    url = f"{API_V1_URL}/{_type}/{command}?indicator={formatted_indicator}&size={size}"

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["annual_statistic"]
        raise_exception_with_valid_request(e, url, valid_request)


INDICATOR_MAP_TYPE = MAP_POLLUTANT_TYPES["indicatorType"]
INDICATOR_MAP = MAP_POLLUTANT_TYPES["indicator"]


def fetch_map_pollutant_concentration_distribution(
    year: int,
    indicatorType: INDICATOR_MAP_TYPE,
    indicator: INDICATOR_MAP,
) -> list:
    """
    limit of 2 requests per minute. Year: 2019 onwards.

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Statystyki%20roczne

    Returns a list of maps of pollutant concentration distributions.
    """

    _type = "concentration"
    command = "getDistributionsOfConcentrationsMap"
    formatted = {
        "indicator": to_url_format(indicator),
        "indicatorType": to_url_format(indicatorType),
    }

    url = (
        f"{API_V1_URL}/{_type}/{command}/"
        f"?year={year}&indicatorType={formatted['indicatorType']}"
        f"&indicator={formatted['indicator']}"
    )

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["map_pollutant"]
        raise_exception_with_valid_request(e, url, valid_request)

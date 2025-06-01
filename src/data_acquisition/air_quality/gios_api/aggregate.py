"""
air quality data from GIOS API:
https://powietrze.gios.gov.pl/pjp/content/api
https://api.gios.gov.pl/pjp-api/swagger-ui/#/

Sensors' data updated:

    hourly:
        - measurement aggregates
"""

# Air quality
from src.data_acquisition.air_quality.request_helpers.fetch_requests import (
    fetch_all_pages,
)
from src.data_acquisition.air_quality.errors import raise_exception_with_valid_request
from src.data_acquisition.air_quality.api_endpoints import (
    API_URL,
    MAX_SIZE,
    GIOS_VALID_API_REQUESTS,
)


def fetch_measurement_aggregates() -> list:
    """
    limit of 2 requests per minute

    https://api.gios.gov.pl/pjp-api/swagger-ui/#/Agregaty%20pomiar%C3%B3w/getAggregatePm10DataUsingGET

    Returns a list of measurement aggregates.
    """

    _type = "aggregate"
    command = "getAggregatePm10Data"
    size = MAX_SIZE
    url = f"{API_URL}/{_type}/{command}?size={size}"

    try:
        return fetch_all_pages(url)
    except Exception as e:
        valid_request = GIOS_VALID_API_REQUESTS["aggregate"]
        raise_exception_with_valid_request(e, url, valid_request)

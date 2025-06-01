"""
Constants for the air quality API data.
"""

# Python
from urllib.parse import urlparse

API_URL = "https://api.gios.gov.pl/pjp-api/rest"
API_V1_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"

MAX_SIZE = 500

# Here you will find the API documentation for the GIOS air quality API.
# Make sure that the IDs are correct and the API is available.
# Sometimes the IDs provided in the documentation are not available.
# https://api.gios.gov.pl/pjp-api/swagger-ui/
GIOS_VALID_API_REQUESTS = {
    "station_data": f"{API_URL}/station/sensors/52",
    "sensor_data": f"{API_URL}station/getSensors/400",
    "annual_statistic": f"{API_V1_URL}/statistics/getStatisticsForPollutants?indicator=SO2",
    "map_pollutant": f"{API_V1_URL}/concentration/getDistributionsOfConcentrationsMap/?year=2020&indicatorType=OZ&indicator=PM10_sr_roczna",
    "aggregate": f"{API_URL}/aggregate/getAggregatePm10Data",
    "current_measurement": f"{API_URL}/data/getData/52",
    "air_quality_index": f"{API_URL}/aqindex/getIndex/52",
    "exceedance_information": f"{API_V1_URL}/station/findAll",
}

# https://api.gios.gov.pl/pjp-api/swagger-ui/#/Statystyki%20roczne%20/getStatisticsUsingGET

ANNUAL_STATISTICS_ARGS = {
    "Sulfur Dioxide": "SO2",
    "Nitrogen Dioxide": "NO2",
    "Nitrogen Oxides": "NOx",
    "Carbon Monoxide": "CO",
    "Ozone": "O3",
    "Benzene": "C6H6",
    "Particulate Matter 10": "PM10",
    "Particulate Matter 2.5": "PM2,5",
    "Lead (PM10)": "Pb(PM10)",
    "Arsenic (PM10)": "As(PM10)",
    "Cadmium (PM10)": "Cd(PM10)",
    "Nickel (PM10)": "Ni(PM10)",
    "Benzo(a)pyrene (PM10)": "BaP(PM10)",
    "Polycyclic Aromatic Hydrocarbons (PM10)": "WWA(PM10)",
    "Ions (PM2.5)": "Jony(PM2,5)",
    "Mercury (Total Gaseous Mercury)": "Hg(TGM)",
    "Formaldehyde": "Formaldehyd",
    "Deposition": "Depozycja",
}

# https://api.gios.gov.pl/pjp-api/swagger-ui/#/Mapy%20rozk%C5%82ad%C3%B3w%20st%C4%99%C5%BCe%C5%84%20zanieczyszcze%C5%84/getDistributionsOfConcentrationsMapUsingGET


# Contrary to the documentation, the API does not support the year 2023 and beyond
_years = list(range(2019, 2022 + 1))

MAP_POLLUTANT_ARGS = {
    "indicatorType": {"Health care indicator": "OZ", "Crop protection": "OR"},
    "indicator": {
        "OZ": {
            "Particulate Matter 10 (annual)": "PM10_sr_roczna",
            "Particulate Matter 2.5 (annual)": "PM25_sr_roczna",
            "Nitrogen Dioxide (annual)": "NO2_sr_roczna",
            "Ozone (3-year)": "O3_3letnia",
            "Benzo(a)pyrene (annual)": "BaP_sr_roczna",
            "Sulfur Dioxide (25-hour max)": "SO2_25h_max",
            "Particulate Matter 10 (36-hour max)": "PM10_36_max",
            "Nitrogen Dioxide (19-hour max)": "NO2_19h_max",
            "Sulfur Dioxide (4-hour max)": "SO2_4_max",
        },
        "OR": {
            "Sulfur Dioxide (annual)": "SO2_sr_roczna",
            "Nitrogen Oxides (annual)": "NOx_sr_roczna",
            "Ozone (5-year)": "O3_5letnia",
        },
    },
    "year": _years,
}


def uri_validator(x: str) -> bool:
    """
    Check if the URL is valid.
    """
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


for key, value in GIOS_VALID_API_REQUESTS.items():
    if not uri_validator(value):
        raise ValueError(f"Invalid URL for {key}: {value}")

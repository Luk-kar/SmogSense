"""
Provides functions to generate URLs for accessing data from 
the General Statistical Office of Poland (GUS) API.
The URLs are used to retrieve categories of causes of death 
and targeted metrics related to death statistics.
The documentation: 
https://api.stat.gov.pl/Home/BdlApi
https://bdl.stat.gov.pl/bdl/dane/podgrup/temat
"""

# https://bdl.stat.gov.pl/api/v1/data/by-variable/72305?&unit-level=0
# https://bdl.stat.gov.pl/api/v1/data/by-variable/72305?&unit-level=3

# Python
from urllib.parse import urlparse, urlencode

API_URL = "https://bdl.stat.gov.pl/api/v1"
SUBJECT_ID_DEATH_TYPES = "P1344"
_TOTAL_MALIGNANT_TUMORS = "75948"
_TOTAL_PEOPLE_BY_REGION = {
    "by-variable": "72305",
    "unit-level": {
        "country": 0,
        "province": 2,
    },
    "page_max": 50,
}

MAX_SIZE = 100
# NOTE: We do not narrow the range of years, because we want to have the most whole data.

# Here you will find the API documentation for the GUS API.
# (General Statistical Office of Poland)
# https://api.stat.gov.pl/Home/BdlApi
GUS_API_URLS = {
    "categories": {"url": f"{API_URL}/Variables", "params": ("subject-id")},
    "targeted_metric": {"url": f"{API_URL}/data/by-variable", "params": ("unit-level")},
    "general-params": {"format": "json", "page-size": MAX_SIZE},
}


def get_list_of_categories_causes_of_death_url(subject_id: str) -> str:
    """
    Get the URL to get the list of categories of causes of death.
    """
    base = GUS_API_URLS["categories"]["url"]

    general_params = "&".join(
        [f"{key}={value}" for key, value in GUS_API_URLS["general-params"].items()]
    )

    return base + f"?subject-id={subject_id}&{general_params}&lang=en"


def create_targeted_metric_url(
    variable_id: str, unit_level: int = 2, page_max: int = None
) -> str:
    """
    Get the URL to get the targeted metric.
    """
    base = GUS_API_URLS["targeted_metric"]["url"]

    # Update general params with custom page size if provided
    general_params = GUS_API_URLS["general-params"].copy()
    if page_max:
        general_params["page-size"] = page_max

    # Encode the parameters into a query string
    query_params = urlencode(general_params)
    query_params += f"&unit-level={unit_level}"

    return f"{base}/{variable_id}?{query_params}"


def test_example_urls():
    """
    Test the example URLs.
    """

    # fmt: off
    example_generated = {
        (
            "https://bdl.stat.gov.pl/api/v1/Variables?subject-id=P1344&format=json&page-size=100&lang=en"): \
            get_list_of_categories_causes_of_death_url(
                SUBJECT_ID_DEATH_TYPES
            ),
            ("https://bdl.stat.gov.pl/api/v1/data/by-variable/75948?format=json&page-size=100&unit-level=2"): \
            create_targeted_metric_url(
                _TOTAL_MALIGNANT_TUMORS
            ),
            "https://bdl.stat.gov.pl/api/v1/data/by-variable/72305?format=json&page-size=50&unit-level=0": \
            create_targeted_metric_url(
                _TOTAL_PEOPLE_BY_REGION["by-variable"],
                _TOTAL_PEOPLE_BY_REGION["unit-level"]["country"],
                _TOTAL_PEOPLE_BY_REGION["page_max"],
            ),
            "https://bdl.stat.gov.pl/api/v1/data/by-variable/72305?format=json&page-size=50&unit-level=2": \
            create_targeted_metric_url(
                _TOTAL_PEOPLE_BY_REGION["by-variable"],
                _TOTAL_PEOPLE_BY_REGION["unit-level"]["province"],
                _TOTAL_PEOPLE_BY_REGION["page_max"],
            ),
    }
    # fmt: on

    for example, generated in example_generated.items():

        try:

            assert example == generated

            # if error t means that the URL is not valid
            urlparse(generated)

        except AssertionError as e:
            raise AssertionError(f"(!=)\n{example}\n{generated}") from e


test_example_urls()

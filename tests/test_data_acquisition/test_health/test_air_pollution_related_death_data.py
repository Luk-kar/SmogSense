"""
Testing the availability of the GUS (Central Statistical Office) API.
"""

# Python
import unittest
import time
import json

# Third party
import requests

# Air quality
from src.data_acquisition.health.pollution_health_data_fetcher import (
    fetch_air_pollution_related_death_data,
    fetch_province_total_people_yearly_data,
    fetch_country_total_people_yearly_data,
)

try:
    requests.get("https://www.google.com", timeout=10)
except requests.RequestException as e:
    raise Exception("No internet connection.") from e


def verify_api_response(request):
    """
    Sends a GET request to the given URL and verifies the response status code is 200.
    """
    try:
        response = requests.get(request, timeout=10)
        OK = 200
        assert (
            response.status_code == OK
        ), f"GUS API data is not available for:\n{request}"
    except requests.RequestException as e:
        raise AssertionError(f"Request to {request} failed with an exception: {e}")


def test_data_is_not_empty(data):
    """
    Test that the fetched air pollution related data is not empty.
    """
    assert data is not None, "Fetched data is None."
    assert len(data) > 0, "No data returned by the API."


def assert_key_and_nonempty(key, data, error_msg):
    """
    Helper function to assert that a key exists in data and its value is non-empty.
    """
    assert key in data, f"{error_msg}: Key '{key}' is missing."
    assert data[key], f"{error_msg}: Key '{key}' is empty."


class TestGUSAPIAirPollution(unittest.TestCase):
    """
    Tests for GUS API availability and data structure
    for the air pollution related death data.
    This one should be pretty fast.
    """

    data = fetch_air_pollution_related_death_data()

    def tearDown(self):
        """
        Wait 1 second after each test.
        """
        time.sleep(1)

    def test_gus_api_availability(self):
        """
        Test the availability of the GUS API.
        """
        request = "https://bdl.stat.gov.pl/api/v1/data/by-variable/4101?format=json"

        verify_api_response(request)

    def test_data_is_not_empty_wrapper(self):
        """
        Wrapper to call the external test function for data non-emptiness.
        """
        test_data_is_not_empty(self.data)

    def test_json_structure(self):
        """
        Test the structure of the JSON data returned by fetch_air_pollution_related_death_data.
        Verifies:
            - "name" key for the illness (nonempty)
            - "results" key (nonempty list)
            - each 'results' entry has "name" for the province (nonempty)
            - each 'results' entry has "values" (nonempty list)
            - each value in "values" contains nonempty "year" and nonempty "val"
        """

        # self.data is a dictionary, keyed by metric_id
        for metric_id, metric_data in self.data.items():

            # 1. Check "name" for the illness
            assert_key_and_nonempty(
                "name",
                metric_data,
                f"Illness 'name' check failed for metric_id={metric_id}",
            )

            # 2. Check "results" key is present and non-empty
            assert_key_and_nonempty(
                "results",
                metric_data,
                f"'results' check failed for metric_id={metric_id}",
            )

            # 3. Check each result (province data)
            for province_data in metric_data["results"]:
                # 3a. Province 'name'
                assert_key_and_nonempty(
                    "name",
                    province_data,
                    f"Province 'name' check failed in province_data for metric_id={metric_id}",
                )

                # 3b. Check that "values" is present and non-empty
                assert_key_and_nonempty(
                    "values",
                    province_data,
                    f"'values' check failed in province_data for metric_id={metric_id}",
                )

                # 3c. Check each item in "values" for nonempty "year" and "val"
                for value_entry in province_data["values"]:
                    assert_key_and_nonempty(
                        "year",
                        value_entry,
                        f"'year' check failed in value_entry for metric_id={metric_id}",
                    )
                    assert_key_and_nonempty(
                        "val",
                        value_entry,
                        f"'val' check failed in value_entry for metric_id={metric_id}",
                    )


class TestGUSAPIHealth(unittest.TestCase):
    """
    Tests for GUS API availability and data structure
    for the total people yearly data.
    Pretty fast test.
    """

    data_province = fetch_province_total_people_yearly_data()

    data_country = fetch_country_total_people_yearly_data()

    def tearDown(self):
        """
        Wait 1 second after each test.
        """
        time.sleep(1)

    def test_gus_api_availability(self):
        """
        Test the availability of the GUS API.
        """
        request = "https://bdl.stat.gov.pl/api/v1/data/by-variable/72305"

        verify_api_response(request)

    def test_data_is_not_empty_province(self):
        """
        province to call the external test function for data non-emptiness.
        """
        test_data_is_not_empty(self.data_province)

    def test_data_is_not_empty_country(self):
        """
        country to call the external test function for data non-emptiness.
        """
        test_data_is_not_empty(self.data_country)

    def test_json_structure_country(self):
        """
        Test the structure of the JSON data returned by fetch_province_total_people_yearly for country-level data.
        Verifies:
            - "results" key exists and is a nonempty list
            - Each entry in "results" contains:
                - "name" key (nonempty, should be "POLSKA")
                - "values" key (nonempty list)
                - Each item in "values" contains nonempty "year" and "val"
        """

        country_data = list(self.data_country.values())[0]

        # Assuming self.data_country follows the structure of demos_country.json
        assert_key_and_nonempty(
            "results", country_data, "'results' key is missing or empty"
        )

        for year in country_data["results"]:
            # Country name check (should be "POLSKA")
            assert_key_and_nonempty("name", year, "Country 'name' check failed")
            self.assertEqual(
                year["name"], "POLSKA", "Expected country name to be 'POLSKA'"
            )

            # Check "values" is present and non-empty
            assert_key_and_nonempty(
                "values", year, "'values' key missing in country data"
            )

            # Check each item in "values" for nonempty "year" and "val"
            for value_entry in year["values"]:
                assert_key_and_nonempty(
                    "year", value_entry, "'year' key missing in value entry"
                )
                assert_key_and_nonempty(
                    "val", value_entry, "'val' key missing in value entry"
                )

    def test_json_structure_province(self):
        """
        Test the structure of the JSON data returned by fetch_province_total_people_yearly.
        Verifies:
            - "results" key exists and is a nonempty list
            - Each entry in "results" contains:
                - "name" key (nonempty, should be province name)
                - "values" key (nonempty list)
                - Each item in "values" contains nonempty "year" and "val"
        """

        province_data = list(self.data_country.values())[0]

        # Dump the data to a file for debugging
        with open("demos_provinces.json", "w") as f:
            json.dump(province_data, f, indent=4)

        # Check the overall structure
        assert_key_and_nonempty(
            "results", province_data, "'results' key is missing or empty"
        )

        # Iterate over each province's data
        for province in province_data["results"]:
            # Province name check (should be nonempty)
            assert_key_and_nonempty("name", province, "Province 'name' check failed")
            self.assertTrue(province["name"], "Expected province name to be nonempty")

            # Check "values" is present and non-empty
            assert_key_and_nonempty(
                "values", province, "'values' key missing in province data"
            )

            # Check each item in "values" for nonempty "year" and "val"
            for value_entry in province["values"]:
                assert_key_and_nonempty(
                    "year", value_entry, "'year' key missing in value entry"
                )
                assert_key_and_nonempty(
                    "val", value_entry, "'val' key missing in value entry"
                )

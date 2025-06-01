"""
Unit tests for validating multiple requests to the GIOS API.

These tests ensure that the fetched data is not empty and conforms to expected conditions.

For efficiency, the tests utilize random sample sizes and random arguments instead of 
querying all available data from the API.
"""

# Python
import random

# Air quality
from src.data_acquisition.air_quality.gios_api.all_data_fetchers import (
    fetch_sensor_data_all,
    fetch_current_measurement_data_all,
    fetch_fetch_air_quality_index_all,
    fetch_map_pollutants_all,
    fetch_annual_statistics_all,
)
from src.data_acquisition.air_quality.api_endpoints import (
    ANNUAL_STATISTICS_ARGS,
    MAP_POLLUTANT_ARGS,
)

# Tests
from tests.test_data_acquisition.test_air_quality.base_gios_api import BaseTest


class TestCompleteDataFetchers(BaseTest):
    """
    Keep in mind that it takes some time to run the tests.
    Circa 30 seconds for all the tests.
    """

    def test_fetch_sensor_data_all(self):
        """
        Test fetching all sensor data.
        """

        random_sample_size = random.randint(1, 50)
        all_sensor_data = fetch_sensor_data_all(sample=random_sample_size)

        self._assert_non_empty_data(all_sensor_data)

    def test_fetch_current_measurement_data_all(self):
        """
        Test fetching all current measurement data.
        """

        random_sample_size = random.randint(1, 50)
        all_current_measurement_data = fetch_current_measurement_data_all(
            random_sample_size
        )

        self._assert_non_empty_data(all_current_measurement_data)

    def test_fetch_fetch_air_quality_index_all(self):
        """
        Test fetching all air quality index data.
        """

        random_sample_size = random.randint(1, 50)
        all_air_quality_index_data = fetch_fetch_air_quality_index_all(
            random_sample_size
        )

        self._assert_non_empty_data(all_air_quality_index_data)

    def test_fetch_map_pollutants_all(self):
        """
        Test fetching all map pollutants data.
        """

        random_years = self._get_random_years()

        random_indicator_type, random_indicators = self._get_random_indicators()
        indicator_args = {random_indicator_type: random_indicators}

        all_map_pollutants_data = fetch_map_pollutants_all(random_years, indicator_args)

        self._assert_non_empty_data(all_map_pollutants_data)

    def test_fetch_annual_statistics_all(self):
        """
        Test fetching all annual statistics data.
        """

        sampled_items = random.sample(list(ANNUAL_STATISTICS_ARGS.items()), 2)
        random_indicators = dict(sampled_items)

        all_annual_statistics_data = fetch_annual_statistics_all(random_indicators)

        self._assert_non_empty_data(all_annual_statistics_data)

    def _get_random_years(self):
        """
        Selects two random years from the available options.
        """
        return random.sample(MAP_POLLUTANT_ARGS["year"], 2)

    def _get_random_indicators(self):
        """
        Selects a random indicator type and a corresponding random indicator.
        """
        random_indicator_type = random.choice(
            list(MAP_POLLUTANT_ARGS["indicatorType"].values())
        )
        random_indicators = {
            "some_indicator": random.choice(
                list(MAP_POLLUTANT_ARGS["indicator"][random_indicator_type].values())
            )
        }
        return random_indicator_type, random_indicators

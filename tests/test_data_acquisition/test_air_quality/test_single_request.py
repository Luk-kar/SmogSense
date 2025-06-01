"""
Unit tests for validating individual requests to the GIOS API.

These tests ensure that the fetched data is not empty and conforms to expected conditions.

For efficiency, the tests utilize random IDs instead of querying all available data from the API.
"""

# Python
import unittest
import random
from typing import Any


# Air quality
from src.data_acquisition.air_quality.gios_api.aggregate import (
    fetch_measurement_aggregates,
)
from src.data_acquisition.air_quality.gios_api.current import (
    fetch_current_measurement_data,
    fetch_air_quality_index,
    fetch_exceedance_information,
)
from src.data_acquisition.air_quality.gios_api.annual import (
    fetch_station_data,
    fetch_sensor_data,
    fetch_annual_statistics,
    fetch_map_pollutant_concentration_distribution,
)
from src.data_acquisition.air_quality.gios_api.all_data_fetchers import (
    _fetch_station_ids,
    _fetch_sensor_ids,
)
from src.data_acquisition.air_quality.api_endpoints import (
    ANNUAL_STATISTICS_ARGS,
    MAP_POLLUTANT_ARGS,
)

# Tests
from tests.test_data_acquisition.test_air_quality.base_gios_api import BaseTest


class TestAggregate(BaseTest):
    """Verifies the correctness of the measurement aggregates"""

    def test_fetch_measurement_aggregates(self):

        self._test_fetch_data(fetch_measurement_aggregates)


class TestCurrent(BaseTest):
    """Tests real-time data endpoints including current measurements"""

    def test_fetch_current_measurement_data(self):

        self._test_fetch_data_with_random_id(
            _fetch_sensor_ids, fetch_current_measurement_data
        )

    def test_fetch_air_quality_index(self):

        self._test_fetch_data_with_random_id(
            _fetch_station_ids, fetch_air_quality_index
        )

    def test_fetch_exceedance_information(self):

        self._test_fetch_data(fetch_exceedance_information)


class TestAnnual(BaseTest):
    """Focuses on annual data"""

    def test_fetch_station_data(self):

        self._test_fetch_data(fetch_station_data)

    def test_fetch_sensor_data(self):

        self._test_fetch_data_with_random_id(_fetch_station_ids, fetch_sensor_data)

    def test_fetch_annual_statistics(self):

        indicator = self._get_random_annual_statistic_arg()

        data = fetch_annual_statistics(indicator)

        self._assert_non_empty_data(data)

    def test_fetch_map_pollutant_concentration_distribution(self):

        year, indicator_type, indicator = self._get_random_map_pollutant_args()

        data = fetch_map_pollutant_concentration_distribution(
            year=year,
            indicatorType=indicator_type,
            indicator=indicator,
        )

        self._assert_non_empty_data(data)

    def _get_random_annual_statistic_arg(self):

        return _get_random_value_from_dict(ANNUAL_STATISTICS_ARGS)

    def _get_random_map_pollutant_args(self):

        random_year = random.choice(MAP_POLLUTANT_ARGS["year"])

        random_indicator_type = _get_random_value_from_dict(
            MAP_POLLUTANT_ARGS["indicatorType"]
        )

        indicators = MAP_POLLUTANT_ARGS["indicator"][random_indicator_type]

        random_indicator = _get_random_value_from_dict(indicators)

        return random_year, random_indicator_type, random_indicator


def _get_random_value_from_dict(dictionary: dict) -> Any:
    """
    Selects a random value from a dictionary, ignoring the keys.

    How can I get a random key-value pair from a dictionary?
    https://stackoverflow.com/a/4859322

    Returns:
        The randomly selected value from the dictionary.
    """
    _, random_value = random.choice(list(dictionary.items()))
    return random_value


if __name__ == "__main__":
    unittest.main()

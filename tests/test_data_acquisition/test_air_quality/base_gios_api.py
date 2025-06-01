"""
Basic common tests for the GIOS API.
"""

# Python
import random
import unittest


class BaseTest(unittest.TestCase):
    """Base class for the GIOS API tests."""

    def _test_fetch_data(self, fetch_function):
        """Utility method to test fetching data functions."""

        data = fetch_function()
        self._assert_non_empty_data(data)

    def _test_fetch_data_with_random_id(self, fetch_ids_function, fetch_function):
        """Utility method to test fetching data with random ID."""

        ids = fetch_ids_function()
        random_id = random.choice(ids)

        data = fetch_function(random_id)

        self._assert_non_empty_data(data)

    def _assert_non_empty_data(self, data: list):
        """Utility function to assert data is not None and has a length greater than 0."""

        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)

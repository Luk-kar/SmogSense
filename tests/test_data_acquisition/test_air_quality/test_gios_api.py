"""
Testing the availability of the GIOS API.
"""

# Python
import unittest

# Third party
import requests

# Air quality
from src.data_acquisition.air_quality.api_endpoints import GIOS_VALID_API_REQUESTS


class TestGIOSAPI(unittest.TestCase):
    """
    Keep in mind that it takes some time to run the tests.
    Circa 30 seconds for all the tests.
    """

    def test_gios_api_availability(self):
        """
        Test the availability of the GIOS API.
        """

        api_requests = GIOS_VALID_API_REQUESTS

        for request in api_requests.values():

            with self.subTest(request=request):
                try:
                    response = requests.get(request, timeout=31)

                    OK = 200
                    self.assertEqual(
                        response.status_code,
                        OK,
                        f"GIOS API data is not available for:\n{request}",
                    )
                except requests.RequestException as e:
                    self.fail(f"Request to {request} failed with an exception: {e}")


if __name__ == "__main__":
    unittest.main()

"""
Custom exceptions and error handlers 
for the air quality data ingestion pipeline.
"""

# Third-party
from requests.exceptions import RequestException


class FetchOnePageError(Exception):
    """Exception raised for errors in fetching a single page of data from a paginated API."""


class FetchAllPagesError(Exception):
    """Exception raised for errors in fetching paginated API data."""


def raise_exception_with_valid_request(e: Exception, url: str, valid_request: str):
    """
    Raises an exception with a valid request for comparison.
    """

    if url == valid_request:
        raise RequestException(f"An error occurred:\n{e}.\nYour request:{url}") from e

    else:
        raise RequestException(
            f"An error occurred:\n{e}.\n"
            f"Your request:\n{url}\n"
            f"Example request:\n{valid_request}\n"
        ) from e

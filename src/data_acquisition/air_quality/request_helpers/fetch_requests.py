"""
Contains functions for fetching and processing data from a paginated API.
"""

# Python
import json
import random
import time
from typing import Any, Callable, List

# Third-party
import requests
from requests.exceptions import HTTPError, RequestException, Timeout

# Air quality
from src.data_acquisition.air_quality.errors import (
    FetchAllPagesError,
    FetchOnePageError,
)
from src.data_acquisition.air_quality.request_helpers.url_utils import (
    get_page_number,
    update_url_params,
)


def fetch_all_pages(url_source: str, interval: int = 0) -> list:
    """
    Fetches all pages of data from a paginated API.
    """

    try:
        combined_data = []
        current_data = fetch_page(url_source)
        combined_data.append(current_data)

        has_total_pages = "totalPages" in current_data
        valid_total_pages = has_total_pages and (
            current_data["totalPages"] is not None and current_data["totalPages"] > 0
        )
        has_links = "links" in current_data
        has_self_link = has_links and "self" in current_data["links"]
        has_next_link = has_links and "next" in current_data["links"]

        # NOTE DO NOT USE PRINT STATEMENTS IN PRODUCTION IN THE LOOP
        # https://stackoverflow.com/questions/13288185/performance-effect-of-using-print-statements-in-python-script
        if has_total_pages and valid_total_pages and has_self_link and has_next_link:

            total_pages = current_data["totalPages"]
            page_index = get_page_number(current_data["links"]["self"])

            if page_index is not None:

                while page_index < total_pages:

                    # update_url_params used to avoid bug with multiplied params
                    next_page_url = update_url_params(
                        url_source, {"page": page_index + 1}
                    )
                    current_data = fetch_page(next_page_url, interval)
                    page_index = get_page_number(current_data["links"]["self"])

                    combined_data.append(current_data)

        return combined_data

    except requests.RequestException as e:
        raise FetchAllPagesError(f"An error occurred: {e}") from e


def fetch_page(
    url,
    wait: int | float = 0,
    retries: int = 6,
    backoff_factor: int = 1,
    connect_timeout: int = 10,
    read_timeout: int = 30,
    stream_chunk_size: int = 1024,
    stream_timeout: int = 900,  # 15 minutes
) -> dict:
    """
    Fetches a single page of data from a paginated API.
    """

    if wait:
        time.sleep(wait)

    response = None

    for retry in range(retries):
        try:
            # Regular request with timeout
            response = requests.get(url, timeout=(connect_timeout, read_timeout))
            response.raise_for_status()

            if response.text.strip() == "":
                raise ValueError(f"Empty response from server for URL: {url}")

            return response.json()

        except Timeout:
            # To handle memory issues with large responses, stream the response

            try:
                response = requests.get(
                    url, stream=True, timeout=(connect_timeout, stream_timeout)
                )
                response.raise_for_status()

                json_streamed = ""
                for chunk in response.iter_content(chunk_size=stream_chunk_size):
                    if chunk:
                        json_streamed += chunk.decode("utf-8")

                return json.loads(json_streamed)

            except json.JSONDecodeError:
                raise ValueError(
                    f"Failed to decode streamed JSON data from URL: {url}"
                ) from e
            except RequestException as e:
                raise RequestException(f"Streaming request failed: {e}") from e
            except Exception as e:
                raise Exception(f"An unexpected error occurred: {e}") from e

        except HTTPError as e:
            if response.status_code in [429, 500, 502, 503, 504]:
                sleep_time = backoff_factor * (2**retry)
                print(
                    f"HTTP error {response.status_code}."
                    f"Retrying time {retry + 1} in {sleep_time} seconds..."
                )
                time.sleep(sleep_time)
                continue
            else:
                error_json = response.json() if response.content else {}
                raise RequestException(
                    f"HTTP error {response.status_code} for URL: {url}\n"
                    + f"Error message: {error_json}"
                ) from e

        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from server for URL: {url}") from e

    raise FetchOnePageError(
        f"Failed to fetch data after {retries} attempts for URL: {url}"
        + f"\nError message: {response.json() if response.content else 'No error message'}"
    )


def fetch_and_process_data(
    fetch_ids_def: Callable[[], List[int]],
    fetch_data_def: Callable[[int], Any],
    device_ids: List[int] = None,
    sample: int = None,
) -> List[Any]:
    """
    Generic function to fetch and process data.
    """

    if device_ids is None:
        device_ids = fetch_ids_def()

    if sample is not None:
        if sample <= 0:
            raise ValueError("Sample size must be greater than 0")
        if sample > len(device_ids):
            raise ValueError(
                "The number of samples must be less than or equal to the number of IDs"
            )
        device_ids = random.sample(device_ids, sample)

    all_data = []

    for _id in device_ids:
        data = fetch_data_def(_id)
        if data is not None:
            all_data.extend(data)

    return all_data

"""
Updates the URL with new parameters, ensuring no duplicates.
"""

# Python
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote


def update_url_params(url: str, new_params: dict) -> str:
    """
    Updates the URL with new parameters, ensuring no duplicates.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Update or add new parameters
    for key, value in new_params.items():
        query_params[key] = [value]

    rebuild_query_string = urlencode(query_params, doseq=True)
    updated_url = urlunparse(parsed_url._replace(query=rebuild_query_string))

    return updated_url


def query_url_params(url: str, param: str) -> str:
    """
    Extracts a parameter value from a URL.
    """

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    param = query.get(param, [None])[0]
    return param


def get_page_number(url: str) -> int | None:
    """
    Extracts the page number from a URL.
    """

    value = query_url_params(url, "page")

    if value is not None:
        return int(value)
    else:
        return None


def to_url_format(string: str) -> str:
    """
    Replace spaces with hyphens, convert to lowercase, and URL-encode special characters.
    """
    return quote(string)

"""
Download JSON geodata for provinces (Voivodeships) in Poland from a URL.
"""

# Python
import json

# Thrird party
import requests

PROVINCES_URL = "https://gist.githubusercontent.com/Luk-kar/3aefd3f77d288ada85b5f44422b711d8/raw/b0793391ab0478e0d92052d204e7af493a7ecc92/poland_woj.json"


def fetch_provinces_data():
    response = requests.get(PROVINCES_URL, timeout=10)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


# Example usage
if __name__ == "__main__":
    data = fetch_provinces_data()

    with open("provinces.json", "w") as f:
        json.dump(data, f, indent=4)

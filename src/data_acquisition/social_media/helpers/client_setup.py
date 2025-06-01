"""
This module contains the function to setup a connection with the Twikit API.
"""

# Python
import os

# Third-party
from twikit import Client


async def setup_client_connection(user_args: dict[str, str]) -> Client:
    """
    Setup a connection with the Twikit API.
    Preferable time to await the request from the Twitter side
    to avoid blocking the connection.
    """

    # Create a Twikit client
    client = Client(user_args["user_language"])

    await client.login(
        auth_info_1=user_args["username"],
        auth_info_2=user_args["email"],
        password=user_args["password"],
    )
    print("Login successful.")

    cookies_file = "cookies.json"

    # Save/load cookies
    if not os.path.exists(cookies_file):
        client.save_cookies(cookies_file)
        print("Cookies saved.")
    else:
        client.load_cookies(cookies_file)
        print("Cookies loaded.")
    return client

"""
This module provides a helper function to validate the structure and content of a `config.ini` file
for the existing Twitter account.
"""

# Python
from configparser import ConfigParser
import os


def validate_config(file_path: str):
    """
    Validates the structure and content of the `config.ini` file.
    Raises an error with a specific message if validation fails.
    """

    config_name = os.path.basename(file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"The file `{config_name}` does not exist. Did you forget to create it?"
        )

    config = ConfigParser()
    config.read(file_path)

    # Check if the [X] section exists
    if "X" not in config:
        raise ValueError(
            f"The `{config_name}` file is missing the `[X]` section. Did you forget to set it up?"
        )

    # Field checks
    required_fields = {
        "username": "YOUR_USERNAME",
        "password": "YOUR_PASSWORD",
        "email": "YOUR_EMAIL",
        "user_language": "YOUR_LANGUAGE",
    }

    for field, placeholder in required_fields.items():
        if field not in config["X"]:
            raise ValueError(
                f"The `[X]` section in `{config_name}`"
                f"is missing the `{field}` field. Did you forget to add it?"
            )
        value = config["X"][field].strip()
        if not value or value == placeholder:
            raise ValueError(
                f"Did you forget to set up the `{config_name}`?"
                f"Provide the {field} for {placeholder}."
            )

    # Validate user_language format (e.g., `pl-PL`)
    user_language = config["X"]["user_language"].strip()
    if not user_language or len(user_language.split("-")) != 2:
        raise ValueError(
            f"Invalid `user_language` format in `{config_name}`."
            f"It should be in the form `xx-XX` (e.g., `pl-PL`)."
        )

    print(f"The `{config_name}` file is valid and properly configured.")

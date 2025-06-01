"""
This module contains settings and configurations details
for the Twitter's data acquisition process.
"""

# Python
from configparser import ConfigParser
import os

# API
from src.data_acquisition.social_media.helpers.query import Query, PRODUCTION
from src.data_acquisition.social_media.helpers.config import validate_config

# Dynamically resolve the full path for "config.ini" in the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
CONFIG_FILE = os.path.join(parent_dir, "config.ini")
validate_config(CONFIG_FILE)

config = ConfigParser()
config.read(CONFIG_FILE)

# Example query instance for demonstration (adjust as needed)
default_query = Query('"smog"', "pl", "2025-01-13", "2024-09-01")

twits_args = {
    "query": default_query.str,
    "product": PRODUCTION.TOP,
    "count": 20,  # per query
}

user_args = {
    "username": config["X"]["username"],
    "email": config["X"]["email"],
    "password": config["X"]["password"],
    "user_language": config["X"]["user_language"],
}

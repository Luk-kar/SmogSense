"""
This module contains the validations for the 'air quality station' data acquisition.
"""

from . import dataframes, database_upload

pollution_map_validation_all = [dataframes, database_upload]
__all__ = [
    "pollution_map_validation_all",
]

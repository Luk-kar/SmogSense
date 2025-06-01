"""
This module contains the validations for the 'air quality station' data acquisition.
"""

from . import database_upload, dataframes, untransformed_data

station_validation_all = [database_upload, dataframes, untransformed_data]
__all__ = [
    "station_validation_all",
]

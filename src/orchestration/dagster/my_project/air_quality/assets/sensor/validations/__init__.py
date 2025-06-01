"""
This module contains the validations for the 'air quality station' data acquisition.
"""

from . import database_upload, dataframes

sensor_validation_all = [database_upload, dataframes]
__all__ = [
    "sensor_validation_all",
]

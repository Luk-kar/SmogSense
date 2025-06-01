"""
This module contains the validations for the 'air quality station' data acquisition.
"""

from . import database_upload, dataframes

annual_statistics_validation_all = [database_upload, dataframes]
__all__ = [
    "annual_statistics_validation_all",
]

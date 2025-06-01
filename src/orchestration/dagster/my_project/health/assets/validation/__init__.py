"""
This module contains the validations for the 'health_data' tables, including:
"""

from . import database_upload, dataframes, data_acquisition

health_validation_all = [database_upload, dataframes, data_acquisition]
__all__ = [
    "health_validation_all",
]

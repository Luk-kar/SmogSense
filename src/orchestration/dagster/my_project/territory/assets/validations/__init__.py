"""
This module contains the validations for the 'air quality station' data acquisition.
"""

from . import database_upload

territory_validation_all = [database_upload]
__all__ = [
    "territory_validation_all",
]

"""
This module contains the validations for the 'social_media' asset.
"""

from . import database_upload, data_acquisition

social_media_validation_all = [database_upload, data_acquisition]
__all__ = [
    "social_media_validation_all",
]

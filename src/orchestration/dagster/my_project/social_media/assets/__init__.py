"""Data Acquisition Assets Package"""

from . import (
    data_acquisition,
    datalake,
    drop_schema,
)
from .data_processing import data_modeling, data_preprocessing

social_media_assets_all = [
    data_acquisition,
    datalake,
    data_modeling,
    data_preprocessing,
    drop_schema,
]

__all__ = [
    "social_media_assets_all",
]

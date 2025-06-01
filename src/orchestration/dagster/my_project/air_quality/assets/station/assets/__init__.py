"""Data Acquisition Assets Package"""

from . import data_acquisition, database_upload, datalake
from .data_processing import data_preprocessing_assets_all

station_assets_all = [
    data_acquisition,
    database_upload,
    datalake,
] + data_preprocessing_assets_all

__all__ = [
    "station_assets_all",
]

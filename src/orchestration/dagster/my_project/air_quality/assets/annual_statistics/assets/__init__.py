"""Data Acquisition Assets Package"""

from . import data_acquisition, datalake, database_upload
from .data_processing import data_preprocessing_assets_all

annual_statistics_assets_all = [
    data_acquisition,
    datalake,
    database_upload,
] + data_preprocessing_assets_all

__all__ = [
    "annual_statistics_assets_all",
]

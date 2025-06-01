"""Data Acquisition Assets Package"""

from . import data_acquisition, datalake, database_upload, data_modeling


pollution_map_assets_all = [data_acquisition, datalake, database_upload, data_modeling]

__all__ = [
    "pollution_map_assets_all",
]

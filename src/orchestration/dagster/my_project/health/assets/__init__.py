"""Data Acquisition Assets Package"""

from . import (
    data_acquisition,
    datalake,
    data_preprocessing,
    database_upload,
    drop_schema,
)

health_assets_all = [
    data_acquisition,
    datalake,
    data_preprocessing,
    database_upload,
    drop_schema,
]

__all__ = [
    "health_assets_all",
]

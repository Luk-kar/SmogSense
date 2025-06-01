"""Data Acquisition Assets Package"""

from . import province_table, indicator_table, pollutant_table

data_unification_assets_all = [province_table, indicator_table, pollutant_table]

__all__ = [
    "data_unification_assets_all",
]

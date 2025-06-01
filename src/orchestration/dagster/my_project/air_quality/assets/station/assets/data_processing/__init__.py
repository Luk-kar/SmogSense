"""Data processing assets for 'air quality station' data acquisition."""

from . import data_modeling, data_preprocessing

data_preprocessing_assets_all = [data_modeling, data_preprocessing]

__all__ = ["data_preprocessing_assets_all"]

"""Data Acquisition Assets Package"""

from . import (
    data_acquisition,
    data_preprocessing,
    model_training,
    upload_model,
)

models_deployment_assets_all = [
    data_acquisition,
    data_preprocessing,
    model_training,
    upload_model,
]

__all__ = [
    "models_deployment_assets_all",
]

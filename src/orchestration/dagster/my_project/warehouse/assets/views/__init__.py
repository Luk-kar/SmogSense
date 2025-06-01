"""Data Acquisition Assets Package"""

from . import health_pollution, pollution, social_media

views_assets_all = [
    health_pollution,
    pollution,
    social_media,
]

__all__ = [
    "views_assets_all",
]

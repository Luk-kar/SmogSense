"""
Defines Dagster asset jobs for processing air quality station data,
including data acquisition, processing, and uploading operations.
The jobs are built using predefined asset selections grouped by 
pipeline stages such as fetching, processing, and uploading data.
"""

# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from air_quality.assets.constants import UnificationGroups

# Define asset selections
database_unification_assets = AssetSelection.groups(
    UnificationGroups.DATABASE_UNIFICATION
)

# Define asset jobs
air_quality_unify_data_job = define_asset_job(
    name="unify_air_quality_data",
    selection=database_unification_assets,
)

"""
Defines Dagster asset jobs for processing air quality station data,
including data acquisition, processing, and uploading operations.
The jobs are built using predefined asset selections grouped by 
pipeline stages such as fetching, processing, and uploading data.
"""

# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from air_quality.assets.constants import Groups

# Define asset selections
drop_schema_assets = AssetSelection.groups(Groups.DATABASE_DROP_SCHEMA)

# Define asset jobs
air_quality_drop_schema_job = define_asset_job(
    name="air_quality_drop_schema_job",
    selection=drop_schema_assets,
)

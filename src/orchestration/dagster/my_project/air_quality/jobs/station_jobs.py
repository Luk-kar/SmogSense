"""
Defines Dagster asset jobs for processing air quality station data,
including data acquisition, processing, and uploading operations.
The jobs are built using predefined asset selections grouped by 
pipeline stages such as fetching, processing, and uploading data.
"""

# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from air_quality.assets.constants import StationGroups

# Define selections of assets
fetch_and_upload_data_selection = AssetSelection.groups(
    StationGroups.DATA_ACQUISITION, StationGroups.DATALAKE
)
data_processing_data_selection = AssetSelection.groups(StationGroups.DATA_PROCESSING)
database_upload_data_selection = AssetSelection.groups(StationGroups.DATABASE_UPLOAD)
download_process_and_upload_data_selection = AssetSelection.groups(
    StationGroups.DATA_ACQUISITION,
    StationGroups.DATALAKE,
    StationGroups.DATA_PROCESSING,
    StationGroups.DATABASE_UPLOAD,
)

# Define jobs
air_quality_station_fetch_and_upload = define_asset_job(
    name="air_quality_station_fetch_and_upload",
    selection=fetch_and_upload_data_selection,
)

air_quality_station_data_processing = define_asset_job(
    name="air_quality_station_data_processing",
    selection=data_processing_data_selection,
)

air_quality_station_database_upload = define_asset_job(
    name="air_quality_station_database_upload",
    selection=database_upload_data_selection,
)
air_quality_station_download_process_and_upload = define_asset_job(
    name="air_quality_station_download_process_and_upload",
    selection=download_process_and_upload_data_selection,
)

air_quality_station_jobs_all = [
    air_quality_station_fetch_and_upload,
    air_quality_station_data_processing,
    air_quality_station_database_upload,
    air_quality_station_download_process_and_upload,
]

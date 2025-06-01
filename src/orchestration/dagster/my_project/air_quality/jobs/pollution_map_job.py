# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from air_quality.assets.constants import MapPollutantGroups

# Define selections of assets
fetch_and_upload_map_pollutant_selection = AssetSelection.groups(
    MapPollutantGroups.DATA_ACQUISITION, MapPollutantGroups.DATALAKE
)
data_processing_map_pollutant_selection = AssetSelection.groups(
    MapPollutantGroups.DATA_PROCESSING
)
database_upload_map_pollutant_selection = AssetSelection.groups(
    MapPollutantGroups.DATABASE_UPLOAD
)
download_process_and_map_pollutant_statistics_selection = AssetSelection.groups(
    MapPollutantGroups.DATA_ACQUISITION,
    MapPollutantGroups.DATALAKE,
    MapPollutantGroups.DATA_PROCESSING,
    MapPollutantGroups.DATABASE_UPLOAD,
)

# Define jobs
air_quality_map_pollutant_fetch_and_upload = define_asset_job(
    name="air_quality_map_pollutant_fetch_and_upload",
    selection=fetch_and_upload_map_pollutant_selection,
)

air_quality_map_pollutant_data_processing = define_asset_job(
    name="air_quality_map_pollutant_data_processing",
    selection=data_processing_map_pollutant_selection,
)

air_quality_map_pollutant_database_upload = define_asset_job(
    name="air_quality_map_pollutant_database_upload",
    selection=database_upload_map_pollutant_selection,
)

air_quality_map_pollutant_download_process_and_upload = define_asset_job(
    name="air_quality_map_pollutant_download_process_and_upload",
    selection=download_process_and_map_pollutant_statistics_selection,
)

air_quality_map_pollutant_jobs_all = [
    air_quality_map_pollutant_fetch_and_upload,
    air_quality_map_pollutant_data_processing,
    air_quality_map_pollutant_database_upload,
    air_quality_map_pollutant_download_process_and_upload,
]

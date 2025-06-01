# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from air_quality.assets.constants import SensorGroups

# Define selections of assets
fetch_and_upload_sensor_selection = AssetSelection.groups(
    SensorGroups.DATA_ACQUISITION, SensorGroups.DATALAKE
)
data_processing_sensor_selection = AssetSelection.groups(SensorGroups.DATA_PROCESSING)
database_upload_sensor_selection = AssetSelection.groups(SensorGroups.DATABASE_UPLOAD)
download_process_and_sensor_statistics_selection = AssetSelection.groups(
    SensorGroups.DATA_ACQUISITION,
    SensorGroups.DATALAKE,
    SensorGroups.DATA_PROCESSING,
    SensorGroups.DATABASE_UPLOAD,
)

# Define jobs
air_quality_sensor_fetch_and_upload = define_asset_job(
    name="air_quality_sensor_fetch_and_upload",
    selection=fetch_and_upload_sensor_selection,
)

air_quality_sensor_data_processing = define_asset_job(
    name="air_quality_sensor_data_processing",
    selection=data_processing_sensor_selection,
)

air_quality_sensor_database_upload = define_asset_job(
    name="air_quality_sensor_database_upload",
    selection=database_upload_sensor_selection,
)

air_quality_sensor_download_process_and_upload = define_asset_job(
    name="air_quality_sensor_download_process_and_upload",
    selection=download_process_and_sensor_statistics_selection,
)

air_quality_sensor_jobs_all = [
    air_quality_sensor_fetch_and_upload,
    air_quality_sensor_data_processing,
    air_quality_sensor_database_upload,
    air_quality_sensor_download_process_and_upload,
]

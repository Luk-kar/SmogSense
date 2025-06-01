# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from air_quality.assets.constants import AnnualStatisticsGroups

# Define selections of assets
fetch_and_upload_annual_statistics_selection = AssetSelection.groups(
    AnnualStatisticsGroups.DATA_ACQUISITION, AnnualStatisticsGroups.DATALAKE
)
data_processing_annual_statistics_selection = AssetSelection.groups(
    AnnualStatisticsGroups.DATA_PROCESSING
)
database_upload_annual_statistics_selection = AssetSelection.groups(
    AnnualStatisticsGroups.DATABASE_UPLOAD
)
download_process_and_upload_annual_statistics_selection = AssetSelection.groups(
    AnnualStatisticsGroups.DATA_ACQUISITION,
    AnnualStatisticsGroups.DATALAKE,
    AnnualStatisticsGroups.DATA_PROCESSING,
    AnnualStatisticsGroups.DATABASE_UPLOAD,
)

# Define jobs
air_quality_annual_statistics_fetch_and_upload = define_asset_job(
    name="air_quality_annual_statistics_fetch_and_upload",
    selection=fetch_and_upload_annual_statistics_selection,
)

air_quality_annual_statistics_data_processing = define_asset_job(
    name="air_quality_annual_statistics_data_processing",
    selection=data_processing_annual_statistics_selection,
)

air_quality_annual_statistics_database_upload = define_asset_job(
    name="air_quality_annual_statistics_database_upload",
    selection=database_upload_annual_statistics_selection,
)

air_quality_annual_statistics_download_process_and_upload = define_asset_job(
    name="air_quality_annual_statistics_download_process_and_upload",
    selection=download_process_and_upload_annual_statistics_selection,
)

air_quality_annual_statistics_jobs_all = [
    air_quality_annual_statistics_fetch_and_upload,
    air_quality_annual_statistics_data_processing,
    air_quality_annual_statistics_database_upload,
    air_quality_annual_statistics_download_process_and_upload,
]

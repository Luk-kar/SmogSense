# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from social_media.assets.constants import SocialMediaAssetCategories

# Define selections of assets
fetch_and_upload_social_media_selection = AssetSelection.groups(
    SocialMediaAssetCategories.DATA_ACQUISITION, SocialMediaAssetCategories.DATALAKE
)
data_processing_social_media_selection = AssetSelection.groups(
    SocialMediaAssetCategories.DATA_PROCESSING
)
database_upload_social_media_selection = AssetSelection.groups(
    SocialMediaAssetCategories.DATABASE_UPLOAD
)
download_process_and_upload_social_media_selection = AssetSelection.groups(
    SocialMediaAssetCategories.DATA_ACQUISITION,
    SocialMediaAssetCategories.DATALAKE,
    SocialMediaAssetCategories.DATA_PROCESSING,
    SocialMediaAssetCategories.DATABASE_UPLOAD,
)

# Define jobs
social_media_fetch_and_upload = define_asset_job(
    name="social_media_fetch_and_upload",
    selection=fetch_and_upload_social_media_selection,
)

social_media_data_processing = define_asset_job(
    name="social_media_data_processing",
    selection=data_processing_social_media_selection,
)

social_media_database_upload = define_asset_job(
    name="social_media_database_upload",
    selection=database_upload_social_media_selection,
)

social_media_download_process_and_upload = define_asset_job(
    name="social_media_download_process_and_upload",
    selection=download_process_and_upload_social_media_selection,
)

social_media_jobs_all = [
    social_media_fetch_and_upload,
    social_media_data_processing,
    social_media_database_upload,
    social_media_download_process_and_upload,
]

# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from territory.assets.constants import TerritoryAssetCategories

download_process_and_upload_territory_selection = AssetSelection.groups(
    TerritoryAssetCategories.DATA_ACQUISITION,
    TerritoryAssetCategories.DATALAKE,
    TerritoryAssetCategories.DATA_PROCESSING,
    TerritoryAssetCategories.DATABASE_UPLOAD,
)


territory_download_process_and_upload = define_asset_job(
    name="territory_download_process_and_upload",
    selection=download_process_and_upload_territory_selection,
)

territory_jobs_all = [
    territory_download_process_and_upload,
]

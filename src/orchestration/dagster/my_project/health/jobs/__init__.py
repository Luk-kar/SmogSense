# Dagster
from dagster import AssetSelection, define_asset_job

# Pipeline
from health.constants import HealthGroups

# Define selections of assets
data_acquisition_and_datalake_selection = AssetSelection.groups(
    HealthGroups.DATA_ACQUISITION, HealthGroups.DATALAKE
)
data_processing_selection = AssetSelection.groups(HealthGroups.DATA_PROCESSING)
database_upload_selection = AssetSelection.groups(HealthGroups.DATABASE_UPLOAD)
drop_health_schema_selection = AssetSelection.groups(HealthGroups.DATABASE_DROP_SCHEMA)

comprehensive_health_pipeline_selection = AssetSelection.groups(
    HealthGroups.DATA_ACQUISITION,
    HealthGroups.DATALAKE,
    HealthGroups.DATA_PROCESSING,
    HealthGroups.DATABASE_UPLOAD,
)

health_pipeline_with_database_reset_selection = AssetSelection.groups(
    HealthGroups.DATABASE_DROP_SCHEMA,
    HealthGroups.DATA_ACQUISITION,
    HealthGroups.DATALAKE,
    HealthGroups.DATA_PROCESSING,
    HealthGroups.DATABASE_UPLOAD,
)

# Define jobs
fetch_and_upload_health_job = define_asset_job(
    name="fetch_and_upload_health_job",
    selection=data_acquisition_and_datalake_selection,
)

process_health_data_job = define_asset_job(
    name="process_health_data_job",
    selection=data_processing_selection,
)

upload_health_data_to_database_job = define_asset_job(
    name="upload_health_data_to_database_job",
    selection=database_upload_selection,
)

acquisition_datalake_processing_upload_health_job = define_asset_job(
    name="acquisition_datalake_processing_upload_health_job",
    selection=comprehensive_health_pipeline_selection,
)

yearly_health_job = define_asset_job(
    name="yearly_health_job",
    selection=health_pipeline_with_database_reset_selection,
)

drop_health_schema_job = define_asset_job(
    name="drop_health_schema_job",
    selection=drop_health_schema_selection,
)

health_pipeline_jobs = [
    fetch_and_upload_health_job,
    process_health_data_job,
    upload_health_data_to_database_job,
    yearly_health_job,
    drop_health_schema_job,
    acquisition_datalake_processing_upload_health_job,
]

from dagster import define_asset_job, AssetSelection

# Pipeline
from warehouse.assets.constants import Groups

# Define selections of assets
backup_warehouse_database_selection = AssetSelection.groups(Groups.DATABASE_BACKUP)

monthly_backup_warehouse_db_job = define_asset_job(
    name="monthly_backup_warehouse_db_job",
    selection=backup_warehouse_database_selection,
)

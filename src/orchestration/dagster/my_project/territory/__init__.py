"""
Code responsible for retrieving and uploading data for the administrative division of Poland.
"""

import sys
import os

# Add the parent directory to sys.path to resolve imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Dagster
from dagster import (
    Definitions,
    load_assets_from_modules,
    load_asset_checks_from_modules,
)

# Pipeline
# from territory.jobs import territory_jobs_all as all_jobs

from common.resources import (
    configured_minio_client,
    configured_postgres_resource_psycopg,
    configured_postgres_resource_alchemy,
)

# from territory.assets.validations import territory_validation_all

# Resources

all_resources = {
    "minio_client": configured_minio_client,
    "postgres_psycopg": configured_postgres_resource_psycopg,
    "postgres_alchemy": configured_postgres_resource_alchemy,
}

# All assets and Checks

from territory.assets import (
    data_acquisition,
    datalake,
    data_preprocessing,
    database_upload,
    drop_schema,
)
from territory.assets.validations import territory_validation_all

all_assets_selection = [
    data_acquisition,
    datalake,
    data_preprocessing,
    database_upload,
    drop_schema,
]


all_assets = load_assets_from_modules(all_assets_selection)
all_checks = load_asset_checks_from_modules(territory_validation_all)

# Jobs
from territory.jobs import territory_jobs_all as all_jobs

# # Schedules
from territory.schedules import yearly_territory_data_upload_schedule

defs = Definitions(
    assets=all_assets,
    asset_checks=all_checks,
    resources=all_resources,
    jobs=all_jobs,
    schedules=[yearly_territory_data_upload_schedule],
)

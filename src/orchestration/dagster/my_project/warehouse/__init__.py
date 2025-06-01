"""
In Dagster, a project is a structured collection of code that defines and manages data workflows,
including data processing, scheduling, and monitoring.
It's used to create and maintain data pipelines,
which help automate the flow of data across tasks—such as
cleaning, transforming, and loading data.
Making it useful for teams that need to handle
and manage data in a reliable and repeatable way.
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
    # load_asset_checks_from_modules,
)

# Pipeline

from common.resources import (
    configured_minio_client,
    configured_postgres_resource_psycopg,
    configured_postgres_resource_alchemy,
    configured_github_minio_data_url_resource,
    configured_github_postgres_data_url_resource,
)

# Resources

all_resources = {
    "minio_client": configured_minio_client,
    "postgres_psycopg": configured_postgres_resource_psycopg,
    "postgres_alchemy": configured_postgres_resource_alchemy,
    "github_minio_data": configured_github_minio_data_url_resource,
    "github_postgres_data": configured_github_postgres_data_url_resource,
}

# All assets and Checks

from warehouse.assets import database_backup, upload_example_project_data
from warehouse.assets.views import (
    health_pollution,
    pollution,
    social_media,
)

all_assets_selection = [
    database_backup,
    health_pollution,
    pollution,
    social_media,
    upload_example_project_data,
]

all_assets = load_assets_from_modules(all_assets_selection)

# Schedules
from warehouse.schedules import monthly_warehouse_backup_schedule

defs = Definitions(
    assets=all_assets,
    # asset_checks=all_checks,
    resources=all_resources,
    # jobs=all_jobs,
    schedules=[monthly_warehouse_backup_schedule],
)

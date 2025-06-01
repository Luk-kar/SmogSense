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
    load_asset_checks_from_modules,
)

# Pipeline
from social_media.jobs import social_media_jobs_all as all_jobs

from common.resources import (
    configured_minio_client,
    configured_postgres_resource_psycopg,
    configured_postgres_resource_alchemy,
)

from social_media.assets.validations import social_media_validation_all

# Resources

all_resources = {
    "minio_client": configured_minio_client,
    "postgres_psycopg": configured_postgres_resource_psycopg,
    "postgres_alchemy": configured_postgres_resource_alchemy,
}

# All assets and Checks

from social_media.assets import (
    data_acquisition,
    datalake,
    data_modeling,
    data_preprocessing,
    database_upload,
    drop_schema,
)

all_assets_selection = [
    data_acquisition,
    datalake,
    data_modeling,
    data_preprocessing,
    database_upload,
    drop_schema,
]

all_assets = load_assets_from_modules(all_assets_selection)
all_checks = load_asset_checks_from_modules(social_media_validation_all)

# Schedules
from social_media.schedules import weekly_social_media_schedule

defs = Definitions(
    assets=all_assets,
    asset_checks=all_checks,
    resources=all_resources,
    jobs=all_jobs,
    schedules=[weekly_social_media_schedule],
)

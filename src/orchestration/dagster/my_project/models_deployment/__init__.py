"""
In Dagster, a project is a structured collection of code that defines and manages data workflows, 
including data processing, scheduling, and monitoring.
It's used to create and maintain data pipelines,
which help automate the flow of data across tasks—such as
cleaning, transforming, and loading data.
Making it useful for teams that need to handle
and manage data in a reliable and repeatable way.
"""

# Python
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
from common.resources import (
    configured_minio_client,
    configured_postgres_resource_psycopg,
    configured_postgres_resource_alchemy,
)


# models_deployment
from models_deployment.assets import (
    models_deployment_assets_all,
)

# checks
from models_deployment.assets import validations as all_checks_selection

# Resources
all_resources = {
    "minio_client": configured_minio_client,
    "postgres_psycopg": configured_postgres_resource_psycopg,
    "postgres_alchemy": configured_postgres_resource_alchemy,
}

# All assets and Checks

all_assets = load_assets_from_modules(models_deployment_assets_all)

all_checks = load_asset_checks_from_modules([all_checks_selection])


defs = Definitions(
    assets=all_assets,
    asset_checks=all_checks,
    resources=all_resources,
)

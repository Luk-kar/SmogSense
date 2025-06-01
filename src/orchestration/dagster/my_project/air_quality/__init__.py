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
from air_quality.jobs import air_quality_jobs_all

from common.resources import (
    configured_minio_client,
    configured_postgres_resource_psycopg,
    configured_postgres_resource_alchemy,
)


# Station
from air_quality.assets.station.assets import (
    station_assets_all,
)
from air_quality.assets.station.validations import (
    station_validation_all,
)

# Annual Statistics
from air_quality.assets.annual_statistics.assets import (
    annual_statistics_assets_all,
)
from air_quality.assets.annual_statistics.validations import (
    annual_statistics_validation_all,
)

# Sensor
from air_quality.assets.sensor.assets import (
    sensor_assets_all,
)
from air_quality.assets.sensor.validations import (
    sensor_validation_all,
)

# Map Pollutant
from air_quality.assets.pollution_map.assets import (
    pollution_map_assets_all,
)
from air_quality.assets.pollution_map.validations import (
    pollution_map_validation_all,
)

# Unified Data
from air_quality.assets.data_unification import (
    data_unification_assets_all,
)

# Drop schema
from air_quality.assets import drop_schema


# Air Quality

air_quality_assets = (
    station_assets_all
    + annual_statistics_assets_all
    + sensor_assets_all
    + pollution_map_assets_all
    + data_unification_assets_all
    + [drop_schema]
)

air_quality_checks = (
    station_validation_all
    + annual_statistics_validation_all
    + sensor_validation_all
    + pollution_map_validation_all
)

all_jobs = air_quality_jobs_all


# Resources

all_resources = {
    "minio_client": configured_minio_client,
    "postgres_psycopg": configured_postgres_resource_psycopg,
    "postgres_alchemy": configured_postgres_resource_alchemy,
}

# All assets and Checks

all_assets_selection = air_quality_assets

all_checks_selection = air_quality_checks

all_assets = load_assets_from_modules(all_assets_selection)

all_checks = load_asset_checks_from_modules(all_checks_selection)

# Schedules
from air_quality.schedules import yearly_air_quality_schedule as yearly_schedule

defs = Definitions(
    assets=all_assets,
    asset_checks=all_checks,
    resources=all_resources,
    jobs=all_jobs,
    schedules=[yearly_schedule],
)

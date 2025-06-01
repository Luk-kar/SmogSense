"""
Module for validating the structure and contents of DataFrames 
related to health data using Dagster asset checks.
"""

# Python
from typing import Type

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetKey,
    asset_check,
    AssetCheckResult,
)

# SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta

# Pipeline
from health.models.health_models import Province, DeathIllness, Measurement

# Common
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.validation import (
    check_dataframe_structure,
)


@asset_check(
    asset=AssetKey("lower_characters_in_province_column"),
)
def check_province_dataframe(
    create_dataframe_province: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'province' DataFrame."""

    valid_columns = get_province_dataframe_columns(Province)

    return check_dataframe_structure(
        create_dataframe_province,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("rename_columns_death_illness_data"),
)
def check_death_illness_dataframe(
    create_dataframe_death_illness: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'death_illness' DataFrame."""

    valid_columns = get_province_dataframe_columns(DeathIllness)

    return check_dataframe_structure(
        create_dataframe_death_illness,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("rename_columns_measurement_data"),
)
def check_measurement_dataframe(
    create_dataframe_measurement: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'measurement' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Measurement)

    return check_dataframe_structure(
        create_dataframe_measurement,
        valid_columns,
    )


def get_province_dataframe_columns(model_class: Type[DeclarativeMeta]) -> list[str]:
    """
    Return a list of primary key column names
    for the given SQLAlchemy model class.
    """

    return [column.name for column in model_class.__table__.columns]

"""
Defines Dagster asset checks for validating the structure and quality 
of DataFrames representing 'air quality station' data.
It includes checks for schema conformity, non-empty fields,
and valid geographic coordinates.
"""

# Third-party
import pandas as pd

# Dagster
from dagster import (
    AssetCheckExecutionContext,
    AssetKey,
    Failure,
    asset_check,
    AssetCheckResult,
)


# SQLAlchemy
from sqlalchemy import (
    CheckConstraint,
)
from sqlalchemy.inspection import inspect

# Pipeline
from air_quality.models.station_models import (
    Location,
    Province,
)
from common.utils.ORM import (
    get_model_non_primary_keys_and_non_generated_columns,
)
from common.utils.validation import (
    check_dataframe_structure,
    check_non_empty_dataframe,
)


@asset_check(
    asset=AssetKey("create_dataframe_province"),
)
def check_province_dataframe(
    create_dataframe_province: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'province' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Province)

    return check_dataframe_structure(
        create_dataframe_province,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_area"),
)
def check_area_dataframe(create_dataframe_area: pd.DataFrame) -> AssetCheckResult:
    """Checks the structure of the 'area' DataFrame."""

    valid_columns = ["id_area", "city_district", "city", "county", "province"]

    return check_dataframe_structure(
        create_dataframe_area,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_location"),
)
def check_location_dataframe(
    create_dataframe_location: pd.DataFrame,
) -> AssetCheckResult:
    """Checks the structure of the 'location' DataFrame."""

    valid_columns = get_model_non_primary_keys_and_non_generated_columns(Location)

    return check_dataframe_structure(
        create_dataframe_location,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_station"),
)
def check_station_dataframe(create_dataframe_station: pd.DataFrame) -> AssetCheckResult:
    """Checks the structure of the 'station' DataFrame."""

    valid_columns = [
        "id_station",
        "station_name",
        # The natural foreign keys
        "latitude",
        "longitude",
        "id_area",
        "street_address",
    ]

    return check_dataframe_structure(
        create_dataframe_station,
        valid_columns,
    )


@asset_check(
    asset=AssetKey("create_dataframe_province"),
)
def check_province_not_empty_strings(
    create_dataframe_province: pd.DataFrame,
) -> AssetCheckResult:
    """
    Checks if 'province' DataFrame has non-empty values in the 'province' column.
    """

    return check_non_empty_dataframe(create_dataframe_province)


@asset_check(
    asset=AssetKey("create_dataframe_area"),
)
def check_area_not_empty_strings(
    create_dataframe_area: pd.DataFrame,
) -> AssetCheckResult:
    """
    Checks if 'area' DataFrame has non-empty values in the 'city_district' column.
    """

    return check_non_empty_dataframe(create_dataframe_area)


@asset_check(
    asset=AssetKey("create_dataframe_location"),
)
def check_location_not_empty_strings(
    create_dataframe_location: pd.DataFrame,
) -> AssetCheckResult:
    """
    Checks if 'location' DataFrame has non-empty values
    in the 'street_address' column.
    """

    return check_non_empty_dataframe(create_dataframe_location)


@asset_check(
    asset=AssetKey("create_dataframe_station"),
)
def check_station_not_empty_strings(
    create_dataframe_station: pd.DataFrame,
) -> AssetCheckResult:
    """
    Checks if 'station' DataFrame has non-empty values in the 'station_name' column.
    """

    return check_non_empty_dataframe(create_dataframe_station)


@asset_check(
    asset=AssetKey("create_dataframe_location"),
    required_resource_keys={"postgres_alchemy"},
)
def verify_location_coordinates(
    context: AssetCheckExecutionContext,
    create_dataframe_location: pd.DataFrame,
) -> AssetCheckResult:
    """
    Validates the 'latitude' and 'longitude' columns in the 'location' DataFrame
    based on the constraints defined in the Location ORM class.
    """

    metadata = {"Total rows": 0, "Validation results": {}}

    try:
        df = create_dataframe_location

        # Inspect the Location class for CheckConstraints
        constraints = inspect(Location).mapped_table.constraints
        check_constraints = [
            c
            for c in constraints
            if isinstance(c, CheckConstraint)
            and ("latitude" in str(c.sqltext) or "longitude" in str(c.sqltext))
        ]

        # Extract the CheckConstraint expressions
        validation_results = {}
        passed = True

        for constraint in check_constraints:

            # Get the constraint SQL expression
            sql_expr = str(constraint.sqltext)

            # Convert SQL-style expression to Python-compatible expression
            python_expr = sql_expr.replace("AND", "and").replace("OR", "or")

            context.log.info(f"Evaluating constraint: {python_expr}")

            # Apply the constraint to the DataFrame
            try:
                mask = df.eval(python_expr)
                invalid_rows = df[~mask]

                if not invalid_rows.empty:

                    validation_results[constraint.name] = {
                        "Invalid rows": invalid_rows.to_dict(orient="records"),
                        "Invalid count": len(invalid_rows),
                    }

                    passed = False

            except Exception as e:

                context.log.error(f"Error evaluating constraint {constraint.name}: {e}")
                passed = False
                validation_results[constraint.name] = f"Failed to evaluate: {e}"

                # Create metadata for the check result
                metadata = {
                    "Total rows": len(df),
                    "Validation results": validation_results,
                }

        return AssetCheckResult(
            passed=passed,
            metadata=metadata,
        )

    except Exception as e:
        context.log.error(f"Error validating 'location' data: {e}")
        raise Failure(f"Failed to validate 'location' data: {e}") from e

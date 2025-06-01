"""
Provides Dagster asset checks for validating the structure 
of 'air quality station' data from APIs and MinIO.
It includes utilities to ensure data integrity by checking required fields,
nested structures, and key conformity.
"""

# Python
from typing import Any

# Dagster
from dagster import (
    AssetCheckExecutionContext,
    AssetKey,
    asset_check,
    AssetCheckResult,
)

# Pipeline
from common.utils.normalize import flatten_list


@asset_check(
    asset=AssetKey("download_air_quality_station_data_from_minio"),
)
def validate_minio_air_quality_data_structure(
    context: AssetCheckExecutionContext,
    download_air_quality_station_data_from_minio: Any,  # Union[list, dict]
) -> AssetCheckResult:
    """Check the structure and validity of 'air quality station' data downloaded from MinIO."""
    return validate_air_quality_data_structure(
        context=context,
        fetched_air_quality_records=download_air_quality_station_data_from_minio,
    )


@asset_check(
    asset=AssetKey("download_air_quality_station_data"),
)
def validate_air_quality_data_structure_from_API(
    context: AssetCheckExecutionContext,
    download_air_quality_station_data: Any,  # Union[list, dict]
) -> AssetCheckResult:
    """
    Validates that the 'air quality station' data downloaded
    from the API conforms to the expected structure.
    """
    return validate_air_quality_data_structure(
        context=context,
        fetched_air_quality_records=download_air_quality_station_data,
    )


def validate_air_quality_data_structure(
    context: AssetCheckExecutionContext,
    fetched_air_quality_records: list,
) -> AssetCheckResult:
    """
    Validates that the 'air quality station' data is not empty,
    has the expected structure, and does not contain surplus keys.
    """

    expected_keys = {"id", "stationName", "gegrLat", "gegrLon", "city", "addressStreet"}
    expected_city_keys = {"id", "name", "commune"}
    expected_commune_keys = {"communeName", "districtName", "provinceName"}

    validation_results = {
        "records_checked": 0,
        "missing_keys": [],
        "surplus_keys": [],
        "invalid_structures": 0,
    }

    passed = True

    try:
        if not validate_non_empty_data(context, fetched_air_quality_records):

            passed = False

        else:

            records = flatten_list(fetched_air_quality_records)

            # Loop through each record to validate its structure
            for record in records:

                validation_results["records_checked"] += 1

                keys_passed = validate_record_keys(
                    expected_keys, validation_results, record
                )
                passed = passed and keys_passed

                # Validate nested city and commune structure
                if "city" in record:

                    city_passed = validate_city_commune_structure(
                        expected_city_keys,
                        expected_commune_keys,
                        validation_results,
                        record,
                    )

                    passed = passed and city_passed

                else:
                    validation_results["invalid_structures"] += 1
                    passed = False

    except (KeyError, ValueError, TypeError) as e:
        # Catch specific exceptions related to data processing
        context.log.error(f"Error during validation: {e}")
        return AssetCheckResult(
            passed=False,
            metadata={"Error": f"Validation failed with exception: {e}"},
        )

    except Exception as e:
        # Fallback for unexpected exceptions
        context.log.error(f"Unexpected error during validation: {e}")
        return AssetCheckResult(
            passed=False,
            metadata={"Error": f"Unexpected error during validation: {e}"},
        )

    # Log validation results
    context.log.info(f"Validation completed. Results: {validation_results}")

    return AssetCheckResult(
        passed=passed,
        metadata={
            "Records Checked": validation_results["records_checked"],
            "Missing Keys": validation_results["missing_keys"],
            "Surplus Keys": validation_results["surplus_keys"],
            "Invalid Structures": validation_results["invalid_structures"],
        },
    )


def validate_non_empty_data(
    context: AssetCheckExecutionContext, fetched_air_quality_records: list
) -> bool:
    """Check if the data is non-empty."""

    if not fetched_air_quality_records:

        context.log.error("The data is empty.")
        return False

    return True


def validate_record_keys(
    expected_keys: set,
    validation_results: dict,
    record: dict,
) -> bool:
    """
    Validate the keys of a given record against the expected keys.
    Log missing or surplus keys.
    """

    passed = True

    record_keys = set(record.keys())
    missing_keys = expected_keys - record_keys
    surplus_keys = record_keys - expected_keys

    if missing_keys:
        validation_results["missing_keys"].append(
            {"record_id": record.get("id"), "missing_keys": list(missing_keys)}
        )
        passed = False

    if surplus_keys:
        validation_results["surplus_keys"].append(
            {"record_id": record.get("id"), "surplus_keys": list(surplus_keys)}
        )
        passed = False

    return passed


def validate_city_commune_structure(
    expected_city_keys: set,
    expected_commune_keys: set,
    validation_results: dict,
    record: dict,
) -> bool:
    """
    Validate the keys in the 'city' structure and its nested 'commune'.
    """

    passed = True

    city = record["city"]
    city_keys = set(city.keys())
    city_missing_keys = expected_city_keys - city_keys
    city_surplus_keys = city_keys - expected_city_keys

    if city_missing_keys:
        validation_results["missing_keys"].append(
            {
                "record_id": record.get("id"),
                "city_missing_keys": list(city_missing_keys),
            }
        )
        passed = False

    if city_surplus_keys:
        validation_results["surplus_keys"].append(
            {
                "record_id": record.get("id"),
                "city_surplus_keys": list(city_surplus_keys),
            }
        )
        passed = False

        # Check for commune structure
    if "commune" in city:
        commune = city["commune"]
        commune_keys = set(commune.keys())
        commune_missing_keys = expected_commune_keys - commune_keys
        commune_surplus_keys = commune_keys - expected_commune_keys

        if commune_missing_keys:
            validation_results["missing_keys"].append(
                {
                    "record_id": record.get("id"),
                    "commune_missing_keys": list(commune_missing_keys),
                }
            )
            passed = False

        if commune_surplus_keys:
            validation_results["surplus_keys"].append(
                {
                    "record_id": record.get("id"),
                    "commune_surplus_keys": list(commune_surplus_keys),
                }
            )
            passed = False

    return passed

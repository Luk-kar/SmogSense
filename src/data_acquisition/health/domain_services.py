"""
Domain services and helper functions for processing causes of death data.
"""

from src.data_acquisition.health.death_types_and_regions import DEATH_TYPES


def extract_category_ids(categories_data: dict) -> dict:
    """
    Extract category IDs from the categories data.
    """

    return {item["id"]: item["n1"] for item in categories_data.get("results", [])}


def validate_death_types(targeted_metric_ids: dict):
    """
    Validate that the death types are found in the API response.
    """

    errors = []
    for death_type in DEATH_TYPES:
        if death_type not in targeted_metric_ids.values():
            errors.append(death_type)

    if errors:
        raise ValueError(
            "Death type not found in the API response." + "\n".join(errors)
        )


def filter_air_pollution_death_types(targeted_metric_ids: dict) -> list:
    """
    Filter the death types to only include air pollution-related causes of death.
    """

    AIR_POLLUTION_RELATED_INDEXES = [
        4,  # "malignant neoplasms total",
        6,  # "cancer of the trachea, bronchus and lung",
        13,  # "diseases of the circulatory system, total"
        15,  # "Diseases of the circulatory system - ischaemic heart disease"
        16,  # "Diseases of the circulatory system - cerebrovascular disease"
        17,  # "Diseases of the circulatory system - atherosclerotic vascular"
        18,  # "diseases of the respiratory system, total"
        19,  # "respiratory diseases - pneumonia, bronchitis, emphysema and asthma"
    ]

    selected_death_types = [DEATH_TYPES[i] for i in AIR_POLLUTION_RELATED_INDEXES]

    selected_ids = [
        key
        for key, value in targeted_metric_ids.items()
        if value in selected_death_types
    ]

    return selected_ids


def enrich_metrics_with_name(targeted_metric_ids: dict, targeted_metrics: dict) -> dict:
    """
    Enrich the targeted metrics with the death type name.
    """

    for metric_id, metric_data in targeted_metrics.items():
        death_type_name = targeted_metric_ids.get(metric_id)

        if death_type_name:
            # Create a new dictionary with "death_type_name" as the first key
            updated_metric_data = {"name": death_type_name}

            # Add the existing key-value pairs to the new dictionary
            updated_metric_data.update(metric_data)

            # Replace the original dictionary with the updated one
            targeted_metrics[metric_id] = updated_metric_data

        else:
            raise ValueError(f"Death type name not found for metric ID {metric_id}")

    return targeted_metrics

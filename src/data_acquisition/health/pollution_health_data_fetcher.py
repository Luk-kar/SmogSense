"""
The documentation: 
https://api.stat.gov.pl/Home/BdlApi
https://bdl.stat.gov.pl/bdl/dane/podgrup/temat
"""

if __name__ == "__main__":

    import sys
    from pathlib import Path

    # Set the root directory as the base path
    root_path = (
        Path(__file__).resolve().parents[3]
    )  # Adjust based on the depth of your file
    sys.path.append(str(root_path))

    print(f"Added root path:\n{root_path}")

# Python
import json

# Local
from src.data_acquisition.health.api_endpoints import (
    SUBJECT_ID_DEATH_TYPES,
    _TOTAL_PEOPLE_BY_REGION,
)
from src.data_acquisition.health.domain_services import (
    extract_category_ids,
    validate_death_types,
    filter_air_pollution_death_types,
    enrich_metrics_with_name,
)
from src.data_acquisition.health.api_client import (
    fetch_categories_causes_of_death,
    download_targeted_metrics,
)


def fetch_province_total_people_yearly_data() -> dict:
    """
    Fetch the total number of people in the province yearly.
    """

    return download_targeted_metrics(
        [_TOTAL_PEOPLE_BY_REGION["by-variable"]],
        unit_level=_TOTAL_PEOPLE_BY_REGION["unit-level"]["province"],
        page_max=_TOTAL_PEOPLE_BY_REGION["page_max"],
    )


def fetch_country_total_people_yearly_data() -> dict:
    """
    Fetch the total number of people in the country yearly.
    """

    return download_targeted_metrics(
        [_TOTAL_PEOPLE_BY_REGION["by-variable"]],
        unit_level=_TOTAL_PEOPLE_BY_REGION["unit-level"]["country"],
        page_max=_TOTAL_PEOPLE_BY_REGION["page_max"],
    )


def fetch_air_pollution_related_death_data() -> dict:
    """
    Fetch the correlated air pollution death illness data.
    """

    categories_data = fetch_categories_causes_of_death(SUBJECT_ID_DEATH_TYPES)

    targeted_metric_ids = extract_category_ids(categories_data)

    validate_death_types(targeted_metric_ids)

    selected_ids = filter_air_pollution_death_types(targeted_metric_ids)

    targeted_metrics = download_targeted_metrics(selected_ids, unit_level=2)

    enriched_metrics = enrich_metrics_with_name(targeted_metric_ids, targeted_metrics)

    return enriched_metrics


if __name__ == "__main__":

    data = fetch_air_pollution_related_death_data()

    with open("air_pollution_death_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

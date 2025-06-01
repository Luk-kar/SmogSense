
"""
Contains the assets for views related to  in the warehouse.
"""

# Pipelines
from warehouse.assets.constants import (
    WarehouseCategories as Categories,
    Groups,
)
import warehouse.sql.views.health_pollution as sql_views
from warehouse.assets.utils import get_module_path, execute_sql_view_creation

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)


CHRONIC_ILLNESS_MORTALITY_TRENDS_VIEW = get_module_path(sql_views) / "chronic_illness_mortality_trends.sql"
MEDIAN_POLLUTANT_LEVELS_AND_DEATHS_BY_PROVINCE_YEAR_VIEW = get_module_path(sql_views) / "median_pollutant_levels_and_deaths_by_province_year.sql"

@asset(
    group_name=Groups.HEALTH,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.HEALTH_POLLUTION,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(CHRONIC_ILLNESS_MORTALITY_TRENDS_VIEW),
    },
)
def view_chronic_illness_mortality_trends(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, CHRONIC_ILLNESS_MORTALITY_TRENDS_VIEW)

@asset(
    group_name=Groups.HEALTH,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.HEALTH_POLLUTION,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(MEDIAN_POLLUTANT_LEVELS_AND_DEATHS_BY_PROVINCE_YEAR_VIEW),
    },
)
def view_median_pollutant_levels_and_deaths_by_province_year(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, MEDIAN_POLLUTANT_LEVELS_AND_DEATHS_BY_PROVINCE_YEAR_VIEW)


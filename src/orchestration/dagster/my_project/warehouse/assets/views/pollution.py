
"""
Contains the assets for views related to  in the warehouse.
"""

# Pipelines
from warehouse.assets.constants import (
    WarehouseCategories as Categories,
    Groups,
)
import warehouse.sql.views.pollution as sql_views
from warehouse.assets.utils import get_module_path, execute_sql_view_creation

# Dagster
from dagster import (
    AssetExecutionContext,
    asset,
)


POLLUTANT_CONCENTRATION_MAP_VIEW = get_module_path(sql_views) / "pollutant_concentration_map.sql"
TOP_POLLUTED_PLACES_BY_POLLUTANT_VIEW = get_module_path(sql_views) / "top_polluted_places_by_pollutant.sql"
YEARLY_POLLUTANT_TRENDS_BY_PROVINCE_VIEW = get_module_path(sql_views) / "yearly_pollutant_trends_by_province.sql"

@asset(
    group_name=Groups.POLLUTION,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.POLLUTION,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(POLLUTANT_CONCENTRATION_MAP_VIEW),
    },
)
def view_pollutant_concentration_map(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, POLLUTANT_CONCENTRATION_MAP_VIEW)

@asset(
    group_name=Groups.POLLUTION,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.POLLUTION,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(TOP_POLLUTED_PLACES_BY_POLLUTANT_VIEW),
    },
)
def view_top_polluted_places_by_pollutant(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, TOP_POLLUTED_PLACES_BY_POLLUTANT_VIEW)

@asset(
    group_name=Groups.POLLUTION,
    required_resource_keys={"postgres_alchemy"},
    metadata={
        "categories": [
            Categories.POLLUTION,
            Categories.DATABASE,
            Categories.VIEW,
        ],
        "sql_file": str(YEARLY_POLLUTANT_TRENDS_BY_PROVINCE_VIEW),
    },
)
def view_yearly_pollutant_trends_by_province(context: AssetExecutionContext):
    """
    Executes the SQL query from the given file.
    """
    execute_sql_view_creation(context, YEARLY_POLLUTANT_TRENDS_BY_PROVINCE_VIEW)


"""
Defines categories, groups, and utility functions to organize and manage metadata 
for assets in the Dagster framework. It includes classifications specific to air quality 
data pipelines, such as categories for data acquisition, processing, and database operations.
"""

from common.constants import BaseAssetCategories, BaseGroups


class AssetCategories:
    """Base class for defining categories used to classify assets in the system."""


class AirQualityAssetCategories(BaseAssetCategories):
    """
    Extends the base asset categories with air-quality-specific ones.
    """

    AIR_QUALITY = "air_quality"
    STATION_DATA = "station_data"
    ANNUAL_STATISTICS_DATA = "annual_statistics_data"
    DATABASE_INIT_TABLE = "database_init_table"
    DATABASE_UPDATE_CONSTRAINTS = "database_update_constraints"
    DATABASE_NORMALIZED = "database_normalized"
    PROVINCE_TABLE = "province_table"
    AREA_TABLE = "area_table"
    LOCATION_TABLE = "location_table"
    STATION_TABLE = "station_table"
    ZONE_TYPE_TABLE = "zone_type_table"
    ZONE_TABLE = "zone_table"
    INDICATOR_TABLE = "indicator_pollution_table"
    TIME_AVERAGING_TABLE = "measurement_time_averaging_table"
    MEASUREMENT_TABLE = "measurement_table"
    MEASUREMENT_ANNUAL_TABLE = "measurement_annual_table"
    DATABASE_FACT_TABLE = "database_fact_table"
    SENSOR_DATA = "sensor_data"
    SENSOR_TABLE = "sensor_table"
    MAP_POLLUTANT_TABLE = "map_pollutant_table"
    MAP_MEASUREMENT_TABLE = "map_measurement_table"
    MAP_GEOMETRY_TABLE = "map_geometry_table"
    DATABASE_UNIFICATION = "database_unification"
    DROP_SCHEMA = "drop_schema"

    HEALTH = "health"
    TERRITORY = "territory"


class Groups(BaseGroups):
    """
    Extends the base groups for organizing air quality data pipelines.
    """

    pass


STATION_DATA_EXTENSION = "_station_data"
ANNUAL_DATA_EXTENSION = "_annual_statistics"
SENSOR_DATA_EXTENSION = "_sensor_data"
MAP_POLLUTANT_EXTENSION = "_map_pollutant_data"
UNIFICATION_EXTENSION = "_unification"


class StationGroups:
    """
    Extends Groups with station-specific classifications for organizing data pipelines.
    """

    DATA_ACQUISITION = Groups.DATA_ACQUISITION + STATION_DATA_EXTENSION
    DATA_PROCESSING = Groups.DATA_PROCESSING + STATION_DATA_EXTENSION
    DATALAKE = Groups.DATALAKE + STATION_DATA_EXTENSION
    DATABASE_UPLOAD = Groups.DATABASE_UPLOAD + STATION_DATA_EXTENSION
    DROP_SCHEMA = Groups.DATABASE_DROP_SCHEMA + STATION_DATA_EXTENSION


class AnnualStatisticsGroups:
    """
    Extends Groups with classifications for organizing data pipelines for annual statistics.
    """

    DATA_ACQUISITION = Groups.DATA_ACQUISITION + ANNUAL_DATA_EXTENSION
    DATA_PROCESSING = Groups.DATA_PROCESSING + ANNUAL_DATA_EXTENSION
    DATALAKE = Groups.DATALAKE + ANNUAL_DATA_EXTENSION
    DATABASE_UPLOAD = Groups.DATABASE_UPLOAD + ANNUAL_DATA_EXTENSION
    DROP_SCHEMA = Groups.DATABASE_DROP_SCHEMA + ANNUAL_DATA_EXTENSION


class SensorGroups:
    """
    Extends Groups with classifications for organizing data pipelines for sensor data.
    """

    DATA_ACQUISITION = Groups.DATA_ACQUISITION + SENSOR_DATA_EXTENSION
    DATA_PROCESSING = Groups.DATA_PROCESSING + SENSOR_DATA_EXTENSION
    DATALAKE = Groups.DATALAKE + SENSOR_DATA_EXTENSION
    DATABASE_UPLOAD = Groups.DATABASE_UPLOAD + SENSOR_DATA_EXTENSION
    DROP_SCHEMA = Groups.DATABASE_DROP_SCHEMA + SENSOR_DATA_EXTENSION


class MapPollutantGroups:
    """
    Extends Groups with classifications for organizing data pipelines for map pollutant data.
    """

    DATA_ACQUISITION = Groups.DATA_ACQUISITION + MAP_POLLUTANT_EXTENSION
    DATA_PROCESSING = Groups.DATA_PROCESSING + MAP_POLLUTANT_EXTENSION
    DATALAKE = Groups.DATALAKE + MAP_POLLUTANT_EXTENSION
    DATABASE_UPLOAD = Groups.DATABASE_UPLOAD + MAP_POLLUTANT_EXTENSION
    DROP_SCHEMA = Groups.DATABASE_DROP_SCHEMA + MAP_POLLUTANT_EXTENSION


class UnificationGroups:
    """
    Extends Groups with classifications for organizing data pipelines for unification data.
    """

    DATABASE_UNIFICATION = Groups.DATABASE + UNIFICATION_EXTENSION
    DROP_SCHEMA = Groups.DATABASE_DROP_SCHEMA + UNIFICATION_EXTENSION

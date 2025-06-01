from .station_jobs import air_quality_station_jobs_all
from .annual_statistics_jobs import air_quality_annual_statistics_jobs_all
from .sensor_jobs import air_quality_sensor_jobs_all
from .pollution_map_job import air_quality_map_pollutant_jobs_all
from .unify_jobs import air_quality_unify_data_job
from .drop_schema_job import air_quality_drop_schema_job

air_quality_jobs_all = (
    air_quality_station_jobs_all
    + air_quality_annual_statistics_jobs_all
    + air_quality_sensor_jobs_all
    + air_quality_map_pollutant_jobs_all
    + [air_quality_unify_data_job]  # Just one job
    + [air_quality_drop_schema_job]
)

__all__ = ["air_quality_jobs_all"]

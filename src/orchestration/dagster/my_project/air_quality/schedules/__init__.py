"""
Schedules are Dagster's way of supporting traditional methods of automation,
which allow you to specify when a job should run.
Using schedules, you can define a fixed time interval to run a pipeline,
such as daily, hourly, or Monday at 9:00 AM.
"""

# Dagster
from dagster import ScheduleDefinition, job, op
from dagster._core.execution.context.compute import OpExecutionContext

# Pipeline operations
from air_quality.jobs.station_jobs import (
    air_quality_station_download_process_and_upload as station_job,
)
from air_quality.jobs.annual_statistics_jobs import (
    air_quality_annual_statistics_download_process_and_upload as annual_statistics_job,
)
from air_quality.jobs.sensor_jobs import (
    air_quality_sensor_download_process_and_upload as sensor_job,
)
from air_quality.jobs.unify_jobs import air_quality_unify_data_job as unify_data_job
from air_quality.jobs.drop_schema_job import air_quality_drop_schema_job


@op
def log_job_start(context: OpExecutionContext):
    """
    Logs the start of the yearly air quality job.
    """
    context.log.info("➡️ Starting the yearly air quality upload data job")


@op
def reset_schema_op(context: OpExecutionContext):
    """
    Handles schema reset.
    """
    context.log.info("➡️ Init schema reset")
    air_quality_drop_schema_job()
    context.log.info("✅ Schema reset complete!")


@op
def station_upload_op(context: OpExecutionContext):
    """
    Handles station data download, processing, and upload.
    """
    context.log.info("➡️ Init station data upload")
    station_job()
    context.log.info("✅ Station data upload complete!")


@op
def annual_statistics_upload_op(context: OpExecutionContext):
    """
    Handles annual statistics data download, processing, and upload.
    """
    context.log.info("➡️ Init annual statistics data upload")
    annual_statistics_job()
    context.log.info("✅ Annual statistics data upload complete!")


@op
def sensor_upload_op(context: OpExecutionContext):
    """
    Handles sensor data download, processing, and upload.
    """
    context.log.info("➡️ Init sensor data upload")
    sensor_job()
    context.log.info("✅ Sensor data upload complete!")


@op
def unify_data_op(context: OpExecutionContext):
    """
    Handles data unification.
    """
    context.log.info("➡️ Init data unification")
    unify_data_job()
    context.log.info("✅ Data unification complete!")


@job
def yearly_air_quality_job():
    """
    Executes the air quality data pipeline in sequential order:
    1. Resets the schema.
    2. Uploads station data.
    3. Uploads annual statistics.
    4. Uploads sensor data.
    5. Unifies the data.
    """

    log_job_start()

    reset_schema_op()
    station_upload_op()
    annual_statistics_upload_op()
    sensor_upload_op()

    unify_data_op()


yearly_air_quality_schedule = ScheduleDefinition(
    job=yearly_air_quality_job,
    cron_schedule="0 0 1 1 *",  # Run at midnight on January 1st, https://crontab.guru/every-year
)

"""
Schedules are Dagster's way of supporting traditional methods of automation,
which allow you to specify when a job should run.
Using schedules, you can define a fixed time interval to run a pipeline,
such as daily, hourly, or Monday at 9:00 AM.
"""

# Dagster
from dagster import ScheduleDefinition

# Pipeline
from health.jobs import (
    yearly_health_job as health_pipeline_jobs,
)

yearly_health_data_upload_schedule = ScheduleDefinition(
    job=health_pipeline_jobs,
    cron_schedule="0 2 1 1 *",  # Run on the first day of the year at 2:00 AM, https://crontab.guru/#0_2_1_1_*
)

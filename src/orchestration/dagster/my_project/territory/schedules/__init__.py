"""
Schedules are Dagster's way of supporting traditional methods of automation,
which allow you to specify when a job should run.
Using schedules, you can define a fixed time interval to run a pipeline,
such as daily, hourly, or Monday at 9:00 AM.
"""

# Dagster
from dagster import ScheduleDefinition

# Pipeline
from territory.jobs import territory_download_process_and_upload

yearly_territory_data_upload_schedule = ScheduleDefinition(
    job=territory_download_process_and_upload,
    cron_schedule="0 0 1 1 *",  # Run on the first day of the year at 0:00 AM, https://crontab.guru/#0_2_1_1_*
)

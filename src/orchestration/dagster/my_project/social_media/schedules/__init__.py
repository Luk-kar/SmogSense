"""
Schedules are Dagster's way of supporting traditional methods of automation,
which allow you to specify when a job should run.
Using schedules, you can define a fixed time interval to run a pipeline,
such as daily, hourly, or Monday at 9:00 AM.
"""

# Dagster
from dagster import ScheduleDefinition

# Pipeline operations
from social_media.jobs import social_media_download_process_and_upload


weekly_social_media_schedule = ScheduleDefinition(
    job=social_media_download_process_and_upload,
    cron_schedule="0 3 * * 0",  # Run at At 03:00 on Sundays, https://crontab.guru/#0_3_*_*_0
)

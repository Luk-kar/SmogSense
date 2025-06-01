"""
Schedules are Dagster's way of supporting traditional methods of automation,
which allow you to specify when a job should run.
Using schedules, you can define a fixed time interval to run a pipeline,
such as daily, hourly, or Monday at 9:00 AM.
"""

# Dagster
from dagster import ScheduleDefinition

# Pipeline
from warehouse.jobs import monthly_backup_warehouse_db_job

# Runs at 4:00 on the 1st day of every month
# Cron: minute=0, hour=4, day_of_month=1, every month
monthly_warehouse_backup_schedule = ScheduleDefinition(
    job=monthly_backup_warehouse_db_job,
    cron_schedule="0 4 1 * *",  # https://crontab.guru/#0_4_1_*_*
)

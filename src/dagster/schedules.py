from dagster import ScheduleDefinition
from .jobs import etl_job

etl_schedule = ScheduleDefinition(job=etl_job, cron_schedule="0 2 * * *")

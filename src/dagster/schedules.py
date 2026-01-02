from dagster import build_schedule_from_partitioned_job
from .jobs import etl_job

etl_schedule = build_schedule_from_partitioned_job(
    job=etl_job,
)

from dagster import build_schedule_from_partitioned_job
from .jobs import etl_job

# Agenda a execução diária (padrão 00:00 UTC) baseada na partição do Job
etl_schedule = build_schedule_from_partitioned_job(
    job=etl_job,
)

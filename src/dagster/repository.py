from dagster import Definitions, asset, DailyPartitionsDefinition, AssetExecutionContext
from src.etl.etl import run as run_etl
from .schedules import etl_schedule
from .jobs import etl_job
from .resources import SourceAPIResource, TargetDBResource

daily = DailyPartitionsDefinition(start_date="2025-12-01")

@asset(partitions_def=daily)
def etl_diario(context: AssetExecutionContext, api: SourceAPIResource, db: TargetDBResource):
    day = context.partition_key
    # Usa os resources injetados para rodar o ETL
    run_etl(
        day_str=day,
        api_base_url=api.base_url,
        target_engine=db.get_engine()
    )
    return day

defs = Definitions(
    assets=[etl_diario],
    schedules=[etl_schedule],
    jobs=[etl_job],
    resources={
        "api": SourceAPIResource(),
        "db": TargetDBResource(),
    }
)

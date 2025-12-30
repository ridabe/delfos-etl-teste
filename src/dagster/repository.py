import os
from dagster import Definitions, asset, DailyPartitionsDefinition, AssetExecutionContext
from src.etl.etl import run as run_etl

daily = DailyPartitionsDefinition(start_date="2025-12-01")

@asset(partitions_def=daily)
def etl_diario(context: AssetExecutionContext):
    day = context.asset_partition_key
    run_etl(day, os.getenv("API_BASE_URL", "http://api:8000"))
    return day

defs = Definitions(assets=[etl_diario])

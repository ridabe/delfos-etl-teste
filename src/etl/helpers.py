import httpx
import pandas as pd
from datetime import datetime
from typing import Dict

def fetch_api(base_url: str, day: datetime) -> pd.DataFrame:
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = day.replace(hour=23, minute=59, second=59, microsecond=0)
    params = {"start": start.isoformat(), "end": end.isoformat(), "variables": ["wind_speed", "power"]}
    with httpx.Client() as client:
        resp = client.get(f"{base_url}/data", params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
     # Transforma em DataFrame (Tabela do Pandas)   
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp").sort_index()
    return df

def aggregate_10m(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    out: Dict[str, pd.DataFrame] = {}
    for var in ["wind_speed", "power"]:
        agg = df[var].resample("10min").agg(["mean", "min", "max", "std"]).dropna()
        for metric in ["mean", "min", "max", "std"]:
            name = f"{var}_{metric}_10m"
            out[name] = agg[[metric]].rename(columns={metric: "value"}).reset_index()
    return out

from fastapi import FastAPI, Query, HTTPException
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from .database import engine
from .models import data_table

app = FastAPI()

ALLOWED_VARS = {"wind_speed", "power", "ambient_temprature"}

@app.get("/data")
def get_data(start: datetime, end: Optional[datetime] = None, variables: Optional[List[str]] = Query(None)):
    if end is None:
        end = start.replace(hour=23, minute=59, second=59, microsecond=0)
    cols = [data_table.c.timestamp]
    if not variables:
        vars_sel = ["wind_speed", "power", "ambient_temprature"]
    else:
        vars_sel = []
        for v in variables:
            if v not in ALLOWED_VARS:
                raise HTTPException(status_code=400, detail=f"Variável inválida: {v}")
            vars_sel.append(v)
    for v in vars_sel:
        cols.append(getattr(data_table.c, v))
    stmt = select(*cols).where(data_table.c.timestamp >= start, data_table.c.timestamp <= end).order_by(data_table.c.timestamp)
    with engine.connect() as conn:
        rows = conn.execute(stmt).all()
    result = []
    for r in rows:
        item = {"timestamp": r[0].isoformat()}
        for idx, v in enumerate(vars_sel, start=1):
            item[v] = r[idx]
        result.append(item)
    return result

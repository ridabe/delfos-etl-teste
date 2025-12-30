from sqlalchemy import Table, Column, TIMESTAMP, Float
from .database import metadata

data_table = Table(
    "data",
    metadata,
    Column("timestamp", TIMESTAMP, nullable=False),
    Column("wind_speed", Float, nullable=False),
    Column("power", Float, nullable=False),
    Column("ambient_temprature", Float, nullable=False),
)

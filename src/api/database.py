import os
from sqlalchemy import create_engine, MetaData

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/source_db")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

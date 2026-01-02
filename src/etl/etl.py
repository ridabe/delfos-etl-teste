import os
import argparse #ler comandos do terminal
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from .helpers import fetch_api, aggregate_10m

Base = declarative_base()

class Signal(Base):
    __tablename__ = "signal"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    #Exemplo: ID 1 = "wind_speed_mean_10m

class Data(Base):
    __tablename__ = "data"
    timestamp = Column(TIMESTAMP, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signal.id"), primary_key=True)
    value = Column(Float, nullable=False)

def get_engine():
    url = os.getenv("TARGET_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/target_db")
    return create_engine(url)

def ensure_signals(session, names):
    existing = {s.name: s.id for s in session.query(Signal).filter(Signal.name.in_(list(names))).all()}
    for n in names:
        if n not in existing:
            s = Signal(name=n)
            session.add(s)
            session.flush()
            existing[n] = s.id
    session.commit()
    return existing

def write_aggregates(session, signal_map, aggregates):
    rows = []
    for name, df in aggregates.items():
        sid = signal_map[name]
        for _, row in df.iterrows():
            rows.append(Data(timestamp=row["timestamp"].to_pydatetime(), signal_id=sid, value=float(row["value"])))
    if rows:
        session.bulk_save_objects(rows)
        session.commit()

def run(day_str, api_base_url=None):
    if api_base_url is None:
        api_base_url = os.getenv("API_BASE_URL", "http://api:8000")
    day = datetime.fromisoformat(day_str).date()
    # EXTRAI (Extract)
    # Chama o helpers.py para pegar dados da API
    df = fetch_api(api_base_url, datetime.combine(day, datetime.min.time()))

    # TRANSFORMA (Transform)
    # Chama o helpers.py para calcular médias/min/max
    aggregates = aggregate_10m(df)

     # CARREGA (Load)
    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        # Idempotency: Remove dados existentes para o dia antes de inserir novos
        start_ts = datetime.combine(day, datetime.min.time())
        end_ts = datetime.combine(day, datetime.max.time())
        session.query(Data).filter(Data.timestamp >= start_ts, Data.timestamp <= end_ts).delete()
        session.commit()

        signal_map = ensure_signals(session, aggregates.keys())
        write_aggregates(session, signal_map, aggregates)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--api_base_url", default=os.getenv("API_BASE_URL", "http://api:8000"))
    args = parser.parse_args()
    run(args.date, args.api_base_url)

if __name__ == "__main__":
    main()

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.etl.etl import Base

@pytest.fixture
def sample_raw_data():
    """Gera um DataFrame simulando dados da API (1Hz) para testes de agregação."""
    # 10 minutos de dados = 600 pontos
    periods = 600
    start_time = datetime(2026, 1, 1, 12, 0, 0)
    
    timestamps = [start_time + timedelta(seconds=i) for i in range(periods)]
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'wind_speed': np.random.uniform(10, 20, periods),
        'power': np.random.uniform(100, 200, periods)
    })
    
    # Adicionar alguns valores conhecidos para testar médias exatas
    # Ex: Primeiros 10 segundos de 'wind_speed' = 10.0
    df.loc[0:9, 'wind_speed'] = 10.0
    
    df = df.set_index('timestamp').sort_index()
    
    return df

@pytest.fixture
def db_session():
    """Cria um banco SQLite em memória e retorna uma sessão."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

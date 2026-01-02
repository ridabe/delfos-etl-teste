from src.etl.helpers import aggregate_10m
from src.etl.etl import ensure_signals, Signal
from src.etl.etl import load_data, Data
from datetime import datetime
import pandas as pd

def test_aggregate_10m_structure(sample_raw_data):
    """Testa se a agregação retorna a estrutura correta (dicionário de DataFrames)."""
    aggregates = aggregate_10m(sample_raw_data)
    
    assert isinstance(aggregates, dict)
    
    expected_keys = [
        "wind_speed_mean_10m", "wind_speed_min_10m", "wind_speed_max_10m", "wind_speed_std_10m",
        "power_mean_10m", "power_min_10m", "power_max_10m", "power_std_10m"
    ]
    
    for key in expected_keys:
        assert key in aggregates
        df = aggregates[key]
        assert "value" in df.columns
        assert "timestamp" in df.columns

def test_aggregate_10m_calculation(sample_raw_data):
    """Testa cálculo simples de agregação."""    
    sample_raw_data['wind_speed'] = 10.0
    
    aggregates = aggregate_10m(sample_raw_data)
    
    # Verificar média
    df_mean = aggregates['wind_speed_mean_10m']
    # Como sample_raw_data tem 10min de dados (600s), deve haver 1 linha
    assert len(df_mean) == 1
    assert df_mean.iloc[0]['value'] == 10.0
    
    # Verificar desvio padrão
    df_std = aggregates['wind_speed_std_10m']
    assert df_std.iloc[0]['value'] == 0.0

def test_ensure_signals_creates_new(db_session):
    """Testa se novos sinais são criados no banco."""
    names = ["wind_speed", "power"]
    mapping = ensure_signals(db_session, names)
    
    assert len(mapping) == 2
    assert "wind_speed" in mapping
    assert "power" in mapping
    
    # Verificar no banco
    signals = db_session.query(Signal).all()
    assert len(signals) == 2
    assert {s.name for s in signals} == set(names)

def test_ensure_signals_idempotent(db_session):
    """Testa se ensure_signals não duplica sinais existentes."""
    # Primeira chamada
    ensure_signals(db_session, ["wind_speed"])
    
    # Segunda chamada com um novo e um antigo
    mapping = ensure_signals(db_session, ["wind_speed", "power"])
    
    assert len(mapping) == 2
    
    # Verificar no banco
    signals = db_session.query(Signal).all()
    assert len(signals) == 2 # Não deve ser 3

def test_load_data_idempotency(db_session):
    """Testa se load_data remove dados anteriores do mesmo dia antes de inserir."""
    day = datetime(2026, 1, 1).date()
    
    # Criar um sinal dummy
    signal = Signal(name="test_signal")
    db_session.add(signal)
    db_session.commit()
    sid = signal.id
    
    # Inserir dados "velhos" para o dia
    old_data = Data(
        timestamp=datetime(2026, 1, 1, 10, 0, 0),
        signal_id=sid,
        value=50.0
    )
    db_session.add(old_data)
    
    # Inserir dados de OUTRO dia (não deve ser deletado)
    other_day_data = Data(
        timestamp=datetime(2026, 1, 2, 10, 0, 0),
        signal_id=sid,
        value=99.0
    )
    db_session.add(other_day_data)
    db_session.commit()
    
    # Novos dados para inserir
    new_rows = [{
        "timestamp": datetime(2026, 1, 1, 12, 0, 0),
        "signal_id": sid,
        "value": 100.0
    }]
    
    # Executar load_data
    load_data(db_session, day, new_rows)
    
    # Verificar resultados
    all_data = db_session.query(Data).all()
    
    # Deve ter 2 registros: 1 do outro dia (mantido) e 1 novo (inserido)
    # O registro "velho" de 2026-01-01 deve ter sumido
    assert len(all_data) == 2
    
    timestamps = sorted([d.timestamp for d in all_data])
    assert timestamps[0] == datetime(2026, 1, 1, 12, 0, 0) # Novo
    assert timestamps[1] == datetime(2026, 1, 2, 10, 0, 0) # Outro dia mantido
    
    values = sorted([d.value for d in all_data])
    assert 50.0 not in values
    assert 100.0 in values
    assert 99.0 in values

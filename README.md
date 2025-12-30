# Teste Prático de Data Engineering — Delfos

## Visão Geral
Implementação de um pipeline ETL simplificado com dois bancos PostgreSQL (Fonte e Alvo), uma API FastAPI expondo dados do banco Fonte e um script ETL que consome a API via `httpx`, agrega em janelas de 10 minutos e grava no banco Alvo (SQLAlchemy). Opcionalmente, há orquestração com Dagster.

## Período dos Dados de Fonte
- Período coberto: de `2025-12-01 00:00:00` até `2025-12-10 23:59:00` (10 dias consecutivos)
- Frequência: 1 minuto
- Colunas: `timestamp`, `wind_speed`, `power`, `ambient_temprature`

## Estrutura do Repositório
```
/src
  /api
    main.py
    models.py
    database.py
  /etl
    etl.py
    helpers.py
  /dagster   (opcional)
    repository.py
    jobs.py
    schedules.py
/docker
  docker-compose.yml
  Dockerfile.api
  Dockerfile.etl
  /source_init
    init.sql
requirements.txt
README.md
```

## Como subir os bancos e a API (Docker Compose)
1. Instale Docker e Docker Compose.
2. No diretório `docker`, execute:
   - `docker compose up -d postgres_source postgres_target`
   - Aguarde os healthchecks.
   - `docker compose up -d api`
3. A API estará disponível em `http://localhost:8000`.
   - Rota principal: `GET /data`
   - Parâmetros:
     - `start`: ISO datetime obrigatório
     - `end`: ISO datetime opcional (default: fim do dia de `start`)
     - `variables`: lista opcional (`wind_speed`, `power`, `ambient_temprature`). Se omitido, retorna todas.
   - Exemplo:
     - `http://localhost:8000/data?start=2025-12-05T00:00:00&end=2025-12-05T23:59:00&variables=wind_speed&variables=power`

## Como executar o script ETL
### Via Docker Compose
- No diretório `docker`:
  - `docker compose run --rm etl python -m src.etl.etl --date 2025-12-05`
  - Variáveis usadas:
    - `API_BASE_URL=http://api:8000`
    - `TARGET_DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres_target:5432/target_db`
  - O ETL cria tabelas do banco Alvo via SQLAlchemy e grava agregados:
    - Sinais: `wind_speed_mean_10m`, `wind_speed_min_10m`, `wind_speed_max_10m`, `wind_speed_std_10m` e equivalentes para `power`.
    - Tabela `data` do Alvo: `timestamp`, `signal_id`, `value`.

### Via ambiente local (opcional)
1. Crie venv e instale `requirements.txt`.
2. Exporte:
   - `API_BASE_URL=http://localhost:8000`
   - `TARGET_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5434/target_db`
3. Rode:
   - `python -m src.etl.etl --date 2025-12-05`

## Dagster (Orquestração e UI)
### Execução via Docker
O projeto inclui serviços configurados para rodar a interface visual e o daemon do Dagster.
1. No diretório `docker`, execute:
   - `docker compose up -d dagster_webserver dagster_daemon`
   - Isso também subirá os bancos e a API se não estiverem rodando.
2. Acesse a UI em: `http://localhost:3000`
3. Na UI, você pode:
   - Visualizar o asset `etl_diario`.
   - Materializar partições manualmente.
   - Ativar o schedule `etl_schedule` para execução automática (simulada via daemon).

### Definição
- Asset diário particionado com `start_date=2025-12-01`:
  - `src/dagster/repository.py` define `etl_diario`.
  - `src/dagster/jobs.py` define `etl_job`.
  - `src/dagster/schedules.py` define `etl_schedule` (cron 02:00).

### Execução local (sem Docker)
1. Crie venv e instale `requirements.txt`.
2. Exporte:
   - `API_BASE_URL=http://localhost:8000`
   - `TARGET_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5434/target_db`
3. Na raiz do repo:
   - `dagster dev -f src/dagster/repository.py`

## Observações
- O banco Alvo é criado via SQLAlchemy pelo ETL (`Base.metadata.create_all`).
- O banco Fonte é inicializado via `docker/source_init/init.sql`.
- A coluna `ambient_temprature` usa nome conforme especificação.

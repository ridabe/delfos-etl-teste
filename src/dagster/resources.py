from dagster import ConfigurableResource
from sqlalchemy import create_engine
import os

class SourceAPIResource(ConfigurableResource):
    """Recurso para acesso à fonte de dados (API)."""
    base_url: str = os.getenv("API_BASE_URL", "http://api:8000")

class TargetDBResource(ConfigurableResource):
    """Recurso para acesso ao banco de dados alvo."""
    connection_string: str = os.getenv("TARGET_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@postgres_target:5432/target_db")

    def get_engine(self):
        return create_engine(self.connection_string)

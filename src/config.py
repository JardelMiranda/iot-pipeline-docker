"""Configuração de conexão com o PostgreSQL (valores padrão = docker-compose.yml)."""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def get_engine():
    """Cria o engine do SQLAlchemy a partir de variáveis de ambiente."""
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER", "iot_user"),
        password=os.getenv("POSTGRES_PASSWORD", "iot_pass"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "iot_db"),
    )
    return create_engine(url, pool_pre_ping=True)

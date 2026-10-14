"""
Pipeline de ingestão: CSV (Kaggle) -> pandas -> PostgreSQL.

Uso:
    python src/ingest.py                       # usa data/IOT-temp.csv
    python src/ingest.py --csv caminho/arquivo.csv
"""
import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from config import get_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV = BASE_DIR / "data" / "IOT-temp.csv"
SQL_DIR = BASE_DIR / "sql"

# Nomes das colunas do CSV original -> nomes na tabela
COLUMN_MAP = {
    "id": "reading_id",
    "room_id/id": "room_id",
    "noted_date": "noted_at",
    "temp": "temperature",
    "out/in": "location",
}


def extract(csv_path: Path) -> pd.DataFrame:
    """Lê o CSV bruto."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV não encontrado em {csv_path}. Baixe o dataset no Kaggle "
            "(veja data/README.md)."
        )
    df = pd.read_csv(csv_path)
    print(f"[extract] {len(df):,} linhas lidas de {csv_path.name}")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e padroniza os dados para a tabela temperature_readings."""
    df = df.rename(columns=COLUMN_MAP)

    # Datas no formato dia-mês-ano hora:minuto (ex.: 08-12-2018 09:30)
    df["noted_at"] = pd.to_datetime(df["noted_at"], dayfirst=True, errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")

    # Remove registros inválidos e duplicados exatos
    antes = len(df)
    df = df.dropna(subset=["noted_at", "temperature", "location"])
    df = df.drop_duplicates()
    print(f"[transform] {antes - len(df):,} linhas descartadas (nulas/duplicadas)")

    df["location"] = df["location"].astype(str).str.strip().str.title()  # In / Out
    df["room_id"] = df["room_id"].astype(str).str.strip()
    # Dispositivo lógico: sala + posição do sensor (ex.: "Room Admin-In")
    df["device_id"] = df["room_id"] + "-" + df["location"]

    return df[["reading_id", "room_id", "location", "device_id", "noted_at", "temperature"]]


def ensure_schema(engine) -> None:
    """Garante que tabela e views existam (útil se não usou o docker-compose)."""
    with engine.begin() as conn:
        for script in ("01_schema.sql", "02_views.sql"):
            conn.execute(text((SQL_DIR / script).read_text(encoding="utf-8")))
    print("[schema] tabela e views verificadas")


def load(df: pd.DataFrame, engine) -> None:
    """Carrega os dados no PostgreSQL (recarga completa e idempotente)."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE temperature_readings RESTART IDENTITY"))
    df.to_sql(
        "temperature_readings",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )
    print(f"[load] {len(df):,} linhas inseridas")


def validate(engine) -> None:
    """Confere se os dados foram inseridos e as views respondem."""
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM temperature_readings")).scalar()
        print(f"[validate] temperature_readings: {total:,} registros")
        for view in ("avg_temp_por_dispositivo", "leituras_por_hora", "temp_max_min_por_dia"):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {view}")).scalar()
            print(f"[validate] view {view}: {n} linhas")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestão do CSV IoT no PostgreSQL")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="caminho do CSV")
    args = parser.parse_args()

    engine = get_engine()
    ensure_schema(engine)
    df = transform(extract(args.csv))
    load(df, engine)
    validate(engine)
    print("Pipeline concluído com sucesso.")


if __name__ == "__main__":
    main()

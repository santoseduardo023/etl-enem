"""Conexão com o PostgreSQL."""

from dataclasses import asdict

import psycopg

from enem_pipeline.config import get_db_config


def get_connection(
    dbname: str | None = None, autocommit: bool = False
) -> psycopg.Connection:
    """Abre uma conexão com o PostgreSQL; `dbname` sobrescreve o POSTGRES_DB do .env."""
    params = asdict(get_db_config())
    if dbname is not None:
        params["dbname"] = dbname
    return psycopg.connect(**params, autocommit=autocommit)

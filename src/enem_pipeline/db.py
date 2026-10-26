"""Conexão com o PostgreSQL usando as configurações do .env."""

from dataclasses import asdict

import psycopg

from enem_pipeline.config import get_db_config


def get_connection(
    dbname: str | None = None, autocommit: bool = False
) -> psycopg.Connection:
    """Abre uma conexão com o PostgreSQL.

    Args:
        dbname: database de destino. Se None, usa o POSTGRES_DB do .env.
            Útil para conectar no database 'postgres' e criar o 'enem'.
        autocommit: se True, cada comando é confirmado na hora
            (necessário para CREATE DATABASE).
    """
    params = asdict(get_db_config())
    if dbname is not None:
        params["dbname"] = dbname
    return psycopg.connect(**params, autocommit=autocommit)
"""Cria o database e os schemas da arquitetura medallion (idempotente)."""

import logging

from psycopg import sql

from enem_pipeline.config import PROJECT_ROOT, get_db_config
from enem_pipeline.db import get_connection

logger = logging.getLogger(__name__)

SQL_DIR = PROJECT_ROOT / "sql"


def create_database() -> None:
    dbname = get_db_config().dbname

    # CREATE DATABASE não pode rodar dentro de transação, daí o autocommit
    with get_connection(dbname="postgres", autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
        ).fetchone()

        if exists:
            logger.info("Database '%s' já existe, nada a fazer.", dbname)
            return

        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
        logger.info("Database '%s' criado.", dbname)


def create_schemas() -> None:
    script = SQL_DIR / "create_schemas.sql"
    with get_connection() as conn:
        conn.execute(script.read_text(encoding="utf-8"))
    logger.info("Schemas bronze, silver e gold prontos.")
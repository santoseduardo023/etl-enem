"""Setup do banco: cria o database e os schemas da arquitetura medallion."""

from psycopg import sql

from enem_pipeline.config import PROJECT_ROOT, get_db_config
from enem_pipeline.db import get_connection

SQL_DIR = PROJECT_ROOT / "sql"


def create_database() -> None:
    """Cria o database do projeto se ele ainda não existir (idempotente)."""
    dbname = get_db_config().dbname

    # Conecta no database 'postgres' (sempre existe) e com autocommit,
    # porque CREATE DATABASE não pode rodar dentro de uma transação.
    with get_connection(dbname="postgres", autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
        ).fetchone()

        if exists:
            print(f"Database '{dbname}' já existe, nada a fazer.")
            return

        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
        print(f"Database '{dbname}' criado.")


def create_schemas() -> None:
    """Executa o script SQL que cria os schemas bronze, silver e gold."""
    script = SQL_DIR / "create_schemas.sql"

    # Sem autocommit: os CREATE SCHEMA rodam numa transação só.
    # Ao sair do 'with', o psycopg faz commit (ou rollback, se der erro).
    with get_connection() as conn:
        conn.execute(script.read_text(encoding="utf-8"))

    print("Schemas bronze, silver e gold prontos.")


def main() -> None:
    """Prepara o banco do zero: database + schemas."""
    create_database()
    create_schemas()


if __name__ == "__main__":
    main()
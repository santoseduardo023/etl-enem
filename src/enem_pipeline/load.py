"""Load: cria as tabelas da bronze e carrega os CSVs do INEP com COPY."""

import csv
import time
from pathlib import Path
from psycopg import sql
from enem_pipeline.db import get_connection

CSV_ENCODING = "latin-1"
CSV_DELIMITER = ";"
PG_ENCODING = "LATIN1"  # nome do latin-1 no Postgres
CHUNK_SIZE = 1024 * 1024  # 1 MB
BRONZE_SCHEMA = "bronze"
CONTROL_COLUMNS = sql.SQL(
    "_arquivo_origem text NOT NULL, _carregado_em timestamptz NOT NULL DEFAULT now()"
)

def read_header(csv_path: Path) -> list[str]:
    """Nomes das colunas do CSV, em minúsculas."""
    with open(csv_path, encoding=CSV_ENCODING, newline="") as file:
        header = next(csv.reader(file, delimiter=CSV_DELIMITER))
    return [column.strip().lower() for column in header]


def table_name(kind: str, year: int) -> str:
    return f"{kind.lower()}_{year}"


def build_create_table(table: str, columns: list[str]) -> sql.Composed:
    column_defs = sql.SQL(", ").join(
        sql.SQL("{} text").format(sql.Identifier(column)) for column in columns
    )
    return sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({}, {})").format(
        sql.Identifier(BRONZE_SCHEMA),
        sql.Identifier(table),
        column_defs,
        CONTROL_COLUMNS,
    )


def create_bronze_tables(year: int, csv_files: dict[str, Path]) -> None:
    with get_connection() as conn:
        for kind, csv_path in csv_files.items():
            table = table_name(kind, year)
            conn.execute(build_create_table(table, read_header(csv_path)))
            print(f"Tabela {BRONZE_SCHEMA}.{table} pronta.")


def build_copy(table: str, columns: list[str]) -> sql.Composed:
    return sql.SQL(
        "COPY {}.{} ({}) FROM STDIN (FORMAT csv, DELIMITER {}, HEADER true, ENCODING {})"
    ).format(
        sql.Identifier(BRONZE_SCHEMA),
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.Literal(CSV_DELIMITER),
        sql.Literal(PG_ENCODING),
    )


def load_csv(conn, table: str, csv_path: Path) -> int:
    """Carrega um CSV na tabela da bronze via COPY e retorna o número de linhas."""
    conn.execute(
        sql.SQL("ALTER TABLE {}.{} ALTER COLUMN _arquivo_origem SET DEFAULT {}").format(
            sql.Identifier(BRONZE_SCHEMA),
            sql.Identifier(table),
            sql.Literal(csv_path.name),
        )
    )

    size_mb = csv_path.stat().st_size / 1024**2
    print(f"Carregando {csv_path.name} ({size_mb:.0f} MB)...")

    start = time.perf_counter()
    with conn.cursor() as cur:
        with cur.copy(build_copy(table, read_header(csv_path))) as copy:
            with open(csv_path, "rb") as file:
                while data := file.read(CHUNK_SIZE):
                    copy.write(data)
        rows = cur.rowcount
    elapsed = time.perf_counter() - start

    print(f"{BRONZE_SCHEMA}.{table}: {rows:,} linhas em {elapsed:.1f}s")
    return rows


def load_bronze(year: int, csv_files: dict[str, Path]) -> None:
    create_bronze_tables(year, csv_files)
    with get_connection() as conn:
        for kind, csv_path in csv_files.items():
            load_csv(conn, table_name(kind, year), csv_path)
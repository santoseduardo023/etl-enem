"""Load: cria as tabelas da bronze e carrega os CSVs do INEP com COPY."""

import csv
from pathlib import Path
from psycopg import sql
from enem_pipeline.db import get_connection

CSV_ENCODING = "latin-1"
CSV_DELIMITER = ";"
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



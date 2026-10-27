"""Configuração do pipeline: credenciais do banco (.env), pastas de dados e URLs do INEP."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"

ENEM_URLS = {
    2025: "https://download.inep.gov.br/microdados/microdados_enem_2025.zip",
}

REQUIRED_VARS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str = field(repr=False)  # fora do repr para não vazar em logs


def get_db_config() -> DatabaseConfig:
    """Lê as credenciais do .env e falha com mensagem clara se faltar alguma."""
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(
            f"Variáveis de ambiente ausentes: {', '.join(missing)}. "
            f"Copie o .env.example para .env e preencha os valores "
            f"(esperado em: {PROJECT_ROOT / '.env'})."
        )

    return DatabaseConfig(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

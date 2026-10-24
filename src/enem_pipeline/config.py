"""Configuração: lê credenciais do .env e parâmetros do pipeline (anos, URLs, pastas)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Raiz do projeto: config.py -> enem_pipeline -> src -> etl-enem
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Carrega as variáveis do .env para o ambiente do processo
load_dotenv(PROJECT_ROOT / ".env")

REQUIRED_VARS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)


@dataclass(frozen=True)
class DatabaseConfig:
    """Parâmetros de conexão com o PostgreSQL."""

    host: str
    port: int
    dbname: str
    user: str
    password: str = field(repr=False)  # nunca aparece em print/log


def get_db_config() -> DatabaseConfig:
    """Lê as variáveis do banco e falha com mensagem clara se faltar alguma."""
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
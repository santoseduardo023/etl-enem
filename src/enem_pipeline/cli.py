"""CLI do pipeline: `enem-pipeline setup` e `enem-pipeline run --ano <ano>`."""

import argparse
import logging
import sys
import time

from enem_pipeline.config import ENEM_URLS
from enem_pipeline.extract import download_zip, extract_csvs
from enem_pipeline.load import load_bronze
from enem_pipeline.logging_config import setup_logging
from enem_pipeline.setup_db import create_database, create_schemas

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="enem-pipeline",
        description="Pipeline ETL dos microdados do ENEM para o PostgreSQL.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", help="cria o database e os schemas")

    run = subparsers.add_parser("run", help="baixa, extrai e carrega um ano na bronze")
    run.add_argument(
        "--ano",
        type=int,
        required=True,
        choices=sorted(ENEM_URLS),
        help="ano do ENEM a processar",
    )
    return parser


def setup() -> None:
    create_database()
    create_schemas()


def run(year: int) -> None:
    start = time.perf_counter()
    logger.info("Pipeline ENEM %d: início", year)
    download_zip(year)
    csv_files = extract_csvs(year)
    load_bronze(year, csv_files)
    logger.info("Pipeline ENEM %d: concluído em %.0fs", year, time.perf_counter() - start)


def main() -> None:
    args = build_parser().parse_args()
    setup_logging()

    try:
        if args.command == "setup":
            setup()
        elif args.command == "run":
            run(args.ano)
    except KeyboardInterrupt:
        logger.warning("Execução interrompida pelo usuário.")
        sys.exit(130)
    except Exception:
        logger.exception("Pipeline falhou.")
        sys.exit(1)
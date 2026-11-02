"""Configuração de logging do pipeline: console e arquivo."""

import logging

from enem_pipeline.config import PROJECT_ROOT

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
        ],
    )
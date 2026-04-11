"""Configure structured logging for the pipeline."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.common import config


def setup(name: str = "wowers", level: int = logging.INFO) -> logging.Logger:
    logs_dir = config.logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler
    fh = logging.FileHandler(logs_dir / f"{name}.log")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


def get(name: str = "wowers") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup(name)
    return logger

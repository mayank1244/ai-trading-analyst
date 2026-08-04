"""Centralised logging configuration using loguru."""

import sys
from pathlib import Path
from loguru import logger as _loguru_logger
from app.config.settings import settings

_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "trading_analyst.log"
_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}"
_ROTATION = "10 MB"
_RETENTION = "30 days"
_COMPRESSION = "zip"


def setup_logging() -> None:
    """Initialise loguru handlers."""
    _loguru_logger.remove()

    log_level = "DEBUG" if settings.DEBUG else "INFO"

    _loguru_logger.add(
        sys.stderr,
        format=_LOG_FORMAT,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=settings.DEBUG,
    )

    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    _loguru_logger.add(
        str(_LOG_FILE),
        format=_LOG_FORMAT,
        level=log_level,
        rotation=_ROTATION,
        retention=_RETENTION,
        compression=_COMPRESSION,
        backtrace=True,
        diagnose=settings.DEBUG,
        encoding="utf-8",
    )


def get_logger(name: str):
    """Return a loguru logger bound to the given name."""
    return _loguru_logger.bind(name=name)


setup_logging()
logger = _loguru_logger

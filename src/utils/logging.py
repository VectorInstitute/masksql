"""Logging configuration utilities."""

import contextlib
import os
import sys

from loguru import logger


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def configure_logging() -> None:
    """Configure loguru logger with custom formatting and settings."""
    with contextlib.suppress(Exception):
        logger.remove(0)
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        colorize=True,
        enqueue=True,
        format="<green>{time:HH:mm:ss}[{process.id}] | </green><level> {level}: {message}</level>",
    )

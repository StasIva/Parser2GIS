from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

MAX_LOG_SIZE_BYTES: int = 5 * 1024 * 1024
BACKUP_COUNT: int = 3


def make_rotating_file_handler(
    filename: str,
    max_bytes: int = MAX_LOG_SIZE_BYTES,
    backup_count: int = BACKUP_COUNT,
    encoding: str = "utf-8",
) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=encoding,
    )
    return handler


def update_handler(handler: logging.Handler, log_path: str) -> logging.Handler:
    if isinstance(handler, logging.FileHandler) and not isinstance(handler, RotatingFileHandler):
        rotating = make_rotating_file_handler(log_path)
        rotating.setLevel(handler.level)
        if handler.formatter:
            rotating.setFormatter(handler.formatter)
        return rotating
    return handler

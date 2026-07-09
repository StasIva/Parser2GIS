from __future__ import annotations

import logging
import sys
from pathlib import Path


class AppLogger:
    _logger: logging.Logger | None = None

    @classmethod
    def _ensure(cls) -> logging.Logger:
        if cls._logger is None:
            log_dir = Path.home() / ".parser2gis" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            logger = logging.getLogger("parser2gis")
            logger.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(
                str(log_dir / "app.log"), encoding="utf-8", mode="a"
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                "[%(levelname)s] %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            cls._logger = logger
        return cls._logger

    @classmethod
    def debug(cls, message: str) -> None:
        cls._get().debug(message)

    @classmethod
    def info(cls, message: str) -> None:
        cls._get().info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        cls._get().warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        cls._get().error(message)

    @classmethod
    def exception(cls, message: str) -> None:
        cls._get().exception(message)
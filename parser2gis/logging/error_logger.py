from __future__ import annotations

import logging
from pathlib import Path

from parser2gis.logging.log_rotation import make_rotating_file_handler


class ErrorLogger:
    _logger: logging.Logger | None = None

    @classmethod
    def _get(cls) -> logging.Logger:
        if cls._logger is None:
            log_dir = Path.home() / ".parser2gis" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            logger = logging.getLogger("parser2gis.errors")
            logger.setLevel(logging.ERROR)

            handler = make_rotating_file_handler(
                str(log_dir / "source_errors.log"), encoding="utf-8",
            )
            handler.setLevel(logging.ERROR)
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = False
            cls._logger = logger
        return cls._logger

    @classmethod
    def log(cls, message: str, source: str = "source_2gis") -> None:
        cls._get().error("[%s] %s", source, message)

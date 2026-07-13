from __future__ import annotations

import logging
from pathlib import Path

from parser2gis.logging.log_rotation import make_rotating_file_handler


class ExportLogger:
    _logger: logging.Logger | None = None

    @classmethod
    def _ensure(cls) -> logging.Logger:
        if cls._logger is None:
            log_dir = Path.home() / ".parser2gis" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            logger = logging.getLogger("parser2gis.exports")
            logger.setLevel(logging.INFO)

            handler = make_rotating_file_handler(
                str(log_dir / "exports.log"),
                encoding="utf-8",
            )
            handler.setLevel(logging.INFO)
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
    def log_export(
        cls,
        format_name: str,
        file_path: str,
        record_count: int,
        task_id: int | None = None,
        status: str = "done",
    ) -> None:
        task_info = f" [task={task_id}]" if task_id else ""
        cls._ensure().info(
            "Export %s: format=%s, records=%d, path=%s%s",
            status,
            format_name,
            record_count,
            file_path,
            task_info,
        )

    @classmethod
    def log_error(cls, format_name: str, file_path: str, error: str) -> None:
        cls._ensure().error(
            "Export failed: format=%s, path=%s, error=%s",
            format_name,
            file_path,
            error,
        )

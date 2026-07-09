from __future__ import annotations

import logging
from pathlib import Path


class TaskLogger:
    _loggers: dict[int, logging.Logger] = {}

    @classmethod
    def _get(cls, task_id: int) -> logging.Logger:
        if task_id not in cls._loggers:
            log_dir = Path.home() / ".parser2gis" / "logs" / "tasks"
            log_dir.mkdir(parents=True, exist_ok=True)

            logger = logging.getLogger(f"parser2gis.task.{task_id}")
            logger.setLevel(logging.DEBUG)

            handler = logging.FileHandler(
                str(log_dir / f"task_{task_id}.log"), encoding="utf-8", mode="a"
            )
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = False
            cls._loggers[task_id] = logger
        return cls._loggers[task_id]

    @classmethod
    def debug(cls, task_id: int, message: str) -> None:
        cls._get(task_id).debug(message)

    @classmethod
    def info(cls, task_id: int, message: str) -> None:
        cls._get(task_id).info(message)

    @classmethod
    def warning(cls, task_id: int, message: str) -> None:
        cls._get(task_id).warning(message)

    @classmethod
    def error(cls, task_id: int, message: str) -> None:
        cls._get(task_id).error(message)

    @classmethod
    def close_all(cls) -> None:
        for logger in cls._loggers.values():
            for handler in logger.handlers:
                handler.close()
                logger.removeHandler(handler)
        cls._loggers.clear()
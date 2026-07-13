from __future__ import annotations

import logging
import os
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path
from unittest import mock

from parser2gis.logging import AppLogger, ErrorLogger, ExportLogger, TaskLogger
from parser2gis.logging.log_rotation import (
    BACKUP_COUNT,
    MAX_LOG_SIZE_BYTES,
    make_rotating_file_handler,
    update_handler,
)


class TestLogRotation:
    def test_make_rotating_file_handler_defaults(self) -> None:
        handler = make_rotating_file_handler("/tmp/test.log")
        assert isinstance(handler, RotatingFileHandler)
        assert handler.maxBytes == MAX_LOG_SIZE_BYTES
        assert handler.backupCount == BACKUP_COUNT
        assert handler.encoding == "utf-8"
        assert handler.baseFilename.endswith("test.log")

    def test_make_rotating_file_handler_custom(self) -> None:
        handler = make_rotating_file_handler("/tmp/custom.log", max_bytes=1024, backup_count=5)
        assert handler.maxBytes == 1024
        assert handler.backupCount == 5

    def test_update_handler_upgrades_file_handler(self) -> None:
        plain = logging.FileHandler("/tmp/plain.log")
        plain.setLevel(logging.WARNING)
        fmt = logging.Formatter("%(message)s")
        plain.setFormatter(fmt)

        result = update_handler(plain, "/tmp/rotated.log")
        assert isinstance(result, RotatingFileHandler)
        assert result.level == logging.WARNING
        assert result.formatter._fmt == "%(message)s"

    def test_update_handler_passthrough_rotating(self) -> None:
        rotating = RotatingFileHandler("/tmp/rotating.log")
        result = update_handler(rotating, "/tmp/other.log")
        assert result is rotating

    def test_update_handler_passthrough_stream(self) -> None:
        stream = logging.StreamHandler()
        result = update_handler(stream, "/tmp/stream.log")
        assert result is stream


def _reset_app_logger() -> None:
    AppLogger._logger = None
    logger = logging.getLogger("parser2gis")
    for h in list(logger.handlers):
        logger.removeHandler(h)


def _reset_export_logger() -> None:
    ExportLogger._logger = None
    logger = logging.getLogger("parser2gis.exports")
    for h in list(logger.handlers):
        logger.removeHandler(h)


def _reset_error_logger() -> None:
    ErrorLogger._logger = None
    logger = logging.getLogger("parser2gis.errors")
    for h in list(logger.handlers):
        logger.removeHandler(h)


def _reset_task_logger() -> None:
    TaskLogger._loggers = {}


def _reset_all_loggers() -> None:
    _reset_app_logger()
    _reset_export_logger()
    _reset_error_logger()
    _reset_task_logger()


class TestAppLogger:
    def test_logger_levels_write_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_app_logger()
                AppLogger.debug("debug message")
                AppLogger.info("info message")
                AppLogger.warning("warning message")
                AppLogger.error("error message")

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "app.log")
                assert os.path.isfile(log_file)
                content = open(log_file, encoding="utf-8").read()
                assert "debug message" in content
                assert "info message" in content
                assert "warning message" in content
                assert "error message" in content

    def test_logger_includes_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_app_logger()
                AppLogger.info("timestamp check")

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "app.log")
                content = open(log_file, encoding="utf-8").read()
                assert "202" in content

    def test_exception_does_not_raise(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_app_logger()
                try:
                    raise ValueError("test error")
                except ValueError:
                    AppLogger.exception("caught exception")

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "app.log")
                content = open(log_file, encoding="utf-8").read()
                assert "caught exception" in content
                assert "test error" in content

    def test_uses_rotating_file_handler(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_app_logger()
                AppLogger.info("rotation check")

                logger = AppLogger._ensure()
                file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
                assert len(file_handlers) == 1


class TestExportLogger:
    def test_log_export_writes_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_export_logger()
                ExportLogger.log_export("xlsx", "/tmp/out.xlsx", 42, task_id=1)

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "exports.log")
                assert os.path.isfile(log_file)
                content = open(log_file, encoding="utf-8").read()
                assert "xlsx" in content
                assert "42" in content
                assert "task=1" in content

    def test_log_export_without_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_export_logger()
                ExportLogger.log_export("csv", "/tmp/out.csv", 10)

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "exports.log")
                content = open(log_file, encoding="utf-8").read()
                assert "csv" in content
                assert "task=" not in content

    def test_log_error_writes_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_export_logger()
                ExportLogger.log_error("json", "/tmp/out.json", "permission denied")

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "exports.log")
                content = open(log_file, encoding="utf-8").read()
                assert "Export failed" in content
                assert "permission denied" in content

    def test_uses_rotating_file_handler(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_export_logger()
                ExportLogger.log_export("xlsx", "/tmp/out.xlsx", 1)

                logger = ExportLogger._ensure()
                file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
                assert len(file_handlers) == 1


class TestErrorLogger:
    def test_log_writes_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_error_logger()
                ErrorLogger.log("Something went wrong", source="org_fetcher")

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "source_errors.log")
                assert os.path.isfile(log_file)
                content = open(log_file, encoding="utf-8").read()
                assert "Something went wrong" in content
                assert "org_fetcher" in content

    def test_uses_rotating_file_handler(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                _reset_error_logger()
                ErrorLogger.log("test error")

                logger = ErrorLogger._get()
                file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
                assert len(file_handlers) == 1


class TestTaskLogger:
    def test_logger_creates_per_task_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                TaskLogger.close_all()
                TaskLogger.info(1, "task 1 message")
                TaskLogger.info(2, "task 2 message")

                task1_log = os.path.join(tmpdir, ".parser2gis", "logs", "tasks", "task_1.log")
                task2_log = os.path.join(tmpdir, ".parser2gis", "logs", "tasks", "task_2.log")
                assert os.path.isfile(task1_log)
                assert os.path.isfile(task2_log)

                content1 = open(task1_log, encoding="utf-8").read()
                content2 = open(task2_log, encoding="utf-8").read()
                assert "task 1 message" in content1
                assert "task 2 message" in content2
                assert "task 1 message" not in content2
                assert "task 2 message" not in content1

    def test_multiple_levels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                TaskLogger.close_all()
                TaskLogger.debug(3, "debug message")
                TaskLogger.warning(3, "warning message")
                TaskLogger.error(3, "error message")

                log_file = os.path.join(tmpdir, ".parser2gis", "logs", "tasks", "task_3.log")
                content = open(log_file, encoding="utf-8").read()
                assert "debug message" in content
                assert "warning message" in content
                assert "error message" in content

    def test_close_all_clears_loggers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                TaskLogger.close_all()
                TaskLogger.info(10, "before close")
                assert 10 in TaskLogger._loggers
                TaskLogger.close_all()
                assert TaskLogger._loggers == {}

    def test_uses_rotating_file_handler(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(Path, "home", return_value=Path(tmpdir)):
                TaskLogger.close_all()
                TaskLogger.info(99, "rotation check")

                logger = TaskLogger._get(99)
                file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
                assert len(file_handlers) == 1


class TestPackageExports:
    def test_export_logger_is_exported(self) -> None:
        from parser2gis.logging import __all__

        assert "ExportLogger" in __all__

    def test_all_loggers_importable(self) -> None:
        from parser2gis.logging import AppLogger, ErrorLogger, ExportLogger, TaskLogger

        assert AppLogger is not None
        assert ErrorLogger is not None
        assert ExportLogger is not None
        assert TaskLogger is not None

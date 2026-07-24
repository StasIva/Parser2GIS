from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from parser2gis.services.directory_update_service import (
    DirectoryUpdateResult,
    DirectoryUpdateService,
)
from parser2gis.settings.settings import load_settings
from parser2gis.source_2gis.http_client import HttpClient


class UpdateWorker(QThread):
    progress = Signal(str)
    finished_signal = Signal(DirectoryUpdateResult)

    def run(self) -> None:
        client = HttpClient(delay_ms=200)
        api_key = load_settings().api_key
        try:
            service = DirectoryUpdateService(client, api_key=api_key)
            self.progress.emit("Обновление списка городов...")
            cities_result = service.update_cities()
            self.progress.emit(
                f"Города: {cities_result.cities_found} найдено, "
                f"{cities_result.cities_added} добавлено, "
                f"{cities_result.cities_updated} обновлено"
            )

            self.progress.emit("Обновление списка рубрик...")
            rubrics_result = service.update_rubrics()
            self.progress.emit(
                f"Рубрики: {rubrics_result.rubrics_found} найдено, "
                f"{rubrics_result.rubrics_added} добавлено, "
                f"{rubrics_result.rubrics_updated} обновлено"
            )

            combined = DirectoryUpdateResult(
                cities_found=cities_result.cities_found,
                cities_added=cities_result.cities_added,
                cities_updated=cities_result.cities_updated,
                rubrics_found=rubrics_result.rubrics_found,
                rubrics_added=rubrics_result.rubrics_added,
                rubrics_updated=rubrics_result.rubrics_updated,
                errors=[],
            )
            self.finished_signal.emit(combined)
        except Exception as e:
            self.progress.emit(f"Ошибка: {e}")
            self.finished_signal.emit(DirectoryUpdateResult(0, 0, 0, 0, 0, 0, [str(e)]))
        finally:
            client.close()


class UpdateDirectoryDialog(QDialog):
    def __init__(self, parent: object = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Обновление справочника")
        self.setMinimumSize(500, 350)
        self._setup_ui()
        self._worker: UpdateWorker | None = None

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QLabel("Загрузка актуальных городов и рубрик из 2GIS...")
        header.setWordWrap(True)
        layout.addWidget(header)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(200)
        layout.addWidget(self._log)

        button_layout = QHBoxLayout()
        self._update_btn = QPushButton("Начать обновление")
        self._update_btn.clicked.connect(self._start_update)
        button_layout.addWidget(self._update_btn)

        self._close_btn = QPushButton("Закрыть")
        self._close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._close_btn)

        layout.addLayout(button_layout)

    def _start_update(self) -> None:
        self._update_btn.setEnabled(False)
        self._progress.show()
        self._log.clear()
        self._log.append("Начало обновления...")

        self._worker = UpdateWorker()
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, message: str) -> None:
        self._log.append(message)

    def _on_finished(self, result: DirectoryUpdateResult) -> None:
        self._log.append("")
        self._log.append("Обновление завершено.")
        self._log.append(
            f"Города: {result.cities_added} добавлено, "
            f"{result.cities_updated} обновлено"
        )
        self._log.append(
            f"Рубрики: {result.rubrics_added} добавлено, "
            f"{result.rubrics_updated} обновлено"
        )
        if result.errors:
            self._log.append("")
            self._log.append("Ошибки:")
            for err in result.errors:
                self._log.append(f"  - {err}")
        self._progress.hide()
        self._progress.setRange(0, 1)
        self._update_btn.setText("Обновить ещё раз")
        self._update_btn.setEnabled(True)

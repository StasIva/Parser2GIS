from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QComboBox, QLineEdit, QDialogButtonBox, QFormLayout,
)

from parser2gis.settings.settings import AppSettings, SettingsManager


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent: int = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumSize(400, 300)
        self._original = settings
        self._setup_ui(settings)

    def _setup_ui(self, settings: AppSettings) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._threads_spin = QSpinBox()
        self._threads_spin.setRange(1, 10)
        self._threads_spin.setValue(settings.max_concurrent_tasks)
        form.addRow("Макс. задач:", self._threads_spin)

        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(50, 10000)
        self._delay_spin.setSingleStep(50)
        self._delay_spin.setValue(settings.request_delay_ms)
        self._delay_spin.setSuffix(" мс")
        form.addRow("Задержка запросов:", self._delay_spin)

        self._language_combo = QComboBox()
        self._language_combo.addItems(["ru", "en"])
        self._language_combo.setCurrentText(settings.language)
        form.addRow("Язык:", self._language_combo)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["light", "dark"])
        self._theme_combo.setCurrentText(settings.theme)
        form.addRow("Тема:", self._theme_combo)

        self._data_dir_edit = QLineEdit(settings.data_directory)
        form.addRow("Каталог данных:", self._data_dir_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        self._original.max_concurrent_tasks = self._threads_spin.value()
        self._original.request_delay_ms = self._delay_spin.value()
        self._original.language = self._language_combo.currentText()
        self._original.theme = self._theme_combo.currentText()
        self._original.data_directory = self._data_path_edit.text()
        SettingsManager.save(self._original)
        self.accept()
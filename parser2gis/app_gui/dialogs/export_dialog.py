from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QDialogButtonBox, QFileDialog, QProgressBar,
)


class ExportDialog(QDialog):
    def __init__(self, parent: int = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Экспорт")
        self.setMinimumSize(450, 200)
        self._file_path: str = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(self._create_label("Формат:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["XLSX", "CSV", "JSON"])
        fmt_layout.addWidget(self._format_combo)
        layout.addLayout(fmt_layout)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self._create_label("Файл:"))
        self._path_edit = QLineEdit()
        path_layout.addWidget(self._path_edit)
        browse_btn = QPushButton("Обзор")
        browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_label(self, text: str) -> object:
        from PySide6.QtWidgets import QLabel
        return QLabel(text)

    def _browse(self) -> None:
        ext = self._format_combo.currentText().lower()
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "",
                                             f"{self._format_combo.currentText()} (*.{ext})")
        if path:
            self._path_edit.setText(path)
            self._file_path = path

    def selected_format(self) -> str:
        return self._format_combo.currentText().lower()

    def file_path(self) -> str:
        return self._file_path or self._path_edit.text().strip()

    def show_progress(self, current: int, total: int) -> None:
        self._progress_bar.setVisible(True)
        self._progress_bar.setMaximum(max(total, 1))
        self._progress_bar.setValue(current)
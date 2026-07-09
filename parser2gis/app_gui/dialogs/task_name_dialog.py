from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox,
)


class TaskNameDialog(QDialog):
    def __init__(self, default_name: str = "", parent: int = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Имя задачи")
        self.setMinimumWidth(350)
        self._setup_ui(default_name)

    def _setup_ui(self, default_name: str) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Введите имя задачи:"))
        self._name_edit = QLineEdit(default_name)
        layout.addWidget(self._name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def task_name(self) -> str:
        return self._name_edit.text().strip()
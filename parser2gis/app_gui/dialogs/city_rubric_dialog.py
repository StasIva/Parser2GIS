from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QDialogButtonBox, QLabel,
)


class CityRubricDialog(QDialog):
    def __init__(self, cities: list[dict[str, Any]],
                 rubrics: list[dict[str, Any]], parent: object = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Выбор города и рубрики")
        self.setMinimumSize(400, 500)
        self._result: tuple[int, int] | None = None
        self._setup_ui(cities, rubrics)

    def _setup_ui(self, cities: list[dict[str, Any]],
                  rubrics: list[dict[str, Any]]) -> None:
        layout = QVBoxLayout(self)

        self._city_combo = QTreeWidget()
        self._city_combo.setHeaderLabels(["Город"])
        self._city_combo.setMaximumHeight(150)
        for city in cities:
            item = QTreeWidgetItem([city.get("name", "")])
            item.setData(0, 32, city.get("id"))
            self._city_combo.addTopLevelItem(item)
        layout.addWidget(self._city_combo)

        self._rubric_tree = QTreeWidget()
        self._rubric_tree.setHeaderLabels(["Рубрика"])
        for rubric in rubrics:
            item = QTreeWidgetItem([rubric.get("name", "")])
            item.setData(0, 32, rubric.get("id"))
            self._rubric_tree.addTopLevelItem(item)
            for child in rubric.get("children", []):
                child_item = QTreeWidgetItem([child.get("name", "")])
                child_item.setData(0, 32, child.get("id"))
                item.addChild(child_item)
        layout.addWidget(self._rubric_tree)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        city_item = self._city_combo.currentItem()
        rubric_item = self._rubric_tree.currentItem()
        if city_item and rubric_item:
            self._result = (city_item.data(0, 32), rubric_item.data(0, 32))
            self.accept()

    def result(self) -> tuple[int, int] | None:
        return self._result
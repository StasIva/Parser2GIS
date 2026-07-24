from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

COLUMNS = ["ID", "Имя", "Статус", "Прогресс", "Найдено", "Сохранено", "Ошибки", "Создана"]


def _utc_to_local(utc_str: str) -> str:
    if not utc_str:
        return ""
    try:
        dt_utc = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        dt_local = dt_utc.astimezone()
        return dt_local.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return utc_str


class TaskTableModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self._tasks: list[dict[str, Any]] = []

    def set_tasks(self, tasks: list[dict[str, Any]]) -> None:
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._tasks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        task = self._tasks[index.row()]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return task.get("id", "")
            if col == 1:
                return task.get("name", "")
            if col == 2:
                status = task.get("status", "")
                status_map = {"created": "Создана", "running": "Выполняется",
                              "paused": "Приостановлена", "done": "Завершена",
                              "error": "Ошибка"}
                return status_map.get(status, status)
            if col == 3:
                return task.get("progress", 0)
            if col == 4:
                return task.get("orgs_found", 0)
            if col == 5:
                return task.get("orgs_saved", 0)
            if col == 6:
                return task.get("errors_count", 0)
            if col == 7:
                return _utc_to_local(task.get("created_at", ""))
        if role == Qt.ItemDataRole.TextAlignmentRole and col == 3:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return COLUMNS[section] if section < len(COLUMNS) else ""
        return None

    def get_task(self, row: int) -> dict[str, Any] | None:
        if 0 <= row < len(self._tasks):
            return self._tasks[row]
        return None

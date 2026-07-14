from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from parser2gis.app_gui.controllers.app_controller import AppController
from parser2gis.app_gui.dialogs.city_rubric_dialog import CityRubricDialog
from parser2gis.app_gui.dialogs.export_dialog import ExportDialog
from parser2gis.app_gui.dialogs.settings_dialog import SettingsDialog
from parser2gis.app_gui.dialogs.task_name_dialog import TaskNameDialog
from parser2gis.app_gui.dialogs.update_directory_dialog import UpdateDirectoryDialog
from parser2gis.app_gui.models.task_table_model import TaskTableModel
from parser2gis.app_gui.widgets.progress_delegate import ProgressDelegate
from parser2gis.settings.settings import load_settings


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._controller = AppController()
        self._settings = load_settings()
        self._setup_ui()
        self._connect_signals()
        self._refresh_tasks()

    def _setup_ui(self) -> None:
        self.setWindowTitle("2GIS Parser")
        self.resize(self._settings.ui.window_width, self._settings.ui.window_height)

        icon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._task_table = QTableView()
        self._model = TaskTableModel()
        self._task_table.setModel(self._model)
        self._task_table.setItemDelegateForColumn(3, ProgressDelegate())
        self._task_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._task_table.setAlternatingRowColors(True)
        self._task_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._task_table)

        self._status_bar = QStatusBar()
        self._status_bar.addWidget(QLabel("Готов к работе"))
        self.setStatusBar(self._status_bar)

        self._toolbar = QToolBar("Панель инструментов")
        self.addToolBar(self._toolbar)

        self._create_btn = QPushButton("Создать")
        self._start_btn = QPushButton("Старт")
        self._stop_btn = QPushButton("Стоп")
        self._export_btn = QPushButton("Экспорт")
        self._update_dir_btn = QPushButton("Обновить справочник")
        self._settings_btn = QPushButton("Настройки")

        btn_style = "QPushButton { padding: 6px 12px; }"
        for btn in (
            self._create_btn,
            self._start_btn,
            self._stop_btn,
            self._export_btn,
            self._update_dir_btn,
            self._settings_btn,
        ):
            btn.setStyleSheet(btn_style)
            self._toolbar.addWidget(btn)

    def _connect_signals(self) -> None:
        self._controller.set_on_tasks_changed(self._refresh_tasks)
        self._create_btn.clicked.connect(self._on_create)
        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn.clicked.connect(self._on_stop)
        self._export_btn.clicked.connect(self._on_export)
        self._update_dir_btn.clicked.connect(self._on_update_directory)
        self._settings_btn.clicked.connect(self._on_settings)

    def _refresh_tasks(self) -> None:
        tasks = self._controller.get_tasks()
        self._model.set_tasks(tasks)
        summary = self._controller.get_summary()
        total = sum(summary.values())
        self._status_bar.showMessage(f"Всего задач: {total}")

    def _on_create(self) -> None:
        cities = self._controller.get_cities()
        rubrics = self._controller.get_rubrics_tree()
        dialog = CityRubricDialog(cities, rubrics, self)
        if dialog.exec() != CityRubricDialog.Accepted:
            return
        result = dialog.result()
        if not result:
            return
        city_id, rubric_id = result
        name_dialog = TaskNameDialog(self, self)
        if name_dialog.exec() != TaskNameDialog.Accepted:
            return
        name = name_dialog.task_name()
        if name:
            self._controller.create_task(name, city_id, rubric_id)

    def _on_start(self) -> None:
        index = self._task_table.currentIndex()
        if not index.isValid():
            return
        task = self._model.get_task(index.row())
        if task:
            self._controller.start_task(task.get("id"))

    def _on_stop(self) -> None:
        index = self._task_table.currentIndex()
        if not index.isValid():
            return
        task = self._model.get_task(index.row())
        if task:
            self._controller.stop_task(task.get("id"))

    def _on_export(self) -> None:
        dialog = ExportDialog(self)
        if dialog.exec() == ExportDialog.Accepted:
            self._status_bar.showMessage("Экспорт завершён")

    def _on_update_directory(self) -> None:
        dialog = UpdateDirectoryDialog(self)
        dialog.exec()
        self._refresh_tasks()

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self._settings, self)
        dialog.exec()

    def closeEvent(self, event: object) -> None:
        self._settings.ui.window_width = self.width()
        self._settings.ui.window_height = self.height()
        from parser2gis.settings.settings import SettingsManager

        SettingsManager.save(self._settings)
        super().closeEvent(event)

from __future__ import annotations

from typing import Any, Callable

from parser2gis.services.city_service import CityService
from parser2gis.services.rubric_service import RubricService
from parser2gis.services.task_service import TaskService
from parser2gis.task_manager.manager import TaskManager


class AppController:
    def __init__(self, task_manager: TaskManager | None = None) -> None:
        self._city_service = CityService()
        self._rubric_service = RubricService()
        self._task_service = TaskService()
        self._task_manager = task_manager
        self._on_tasks_changed: Callable[[], None] | None = None
        self._on_progress: Callable[[int, int, int], None] | None = None

        if task_manager:
            task_manager.set_on_progress(self._on_task_progress)

    def set_on_tasks_changed(self, callback: Callable[[], None]) -> None:
        self._on_tasks_changed = callback

    def set_on_progress(self, callback: Callable[[int, int, int], None]) -> None:
        self._on_progress = callback

    def get_tasks(self) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self._task_service.get_all()]

    def get_cities(self) -> list[dict[str, Any]]:
        return [c.to_dict() for c in self._city_service.get_all()]

    def get_rubrics_tree(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self._rubric_service.find_tree()]

    def create_task(self, name: str, city_id: int, rubric_id: int) -> dict[str, Any]:
        task = self._task_service.create(name, city_id, rubric_id)
        if self._on_tasks_changed:
            self._on_tasks_changed()
        return task.to_dict()

    def start_task(self, task_id: int) -> None:
        if self._task_manager:
            self._task_manager.start_task(task_id)
        else:
            self._task_service.update_status(task_id, "running")
        if self._on_tasks_changed:
            self._on_tasks_changed()

    def pause_task(self, task_id: int) -> None:
        self._task_service.update_status(task_id, "paused")
        if self._on_tasks_changed:
            self._on_tasks_changed()

    def stop_task(self, task_id: int) -> None:
        self._task_service.update_status(task_id, "done")
        if self._on_tasks_changed:
            self._on_tasks_changed()

    def _on_task_progress(self, task: Any) -> None:
        if self._on_progress:
            self._on_progress(task.id, task.progress, task.status)
        if self._on_tasks_changed:
            self._on_tasks_changed()

    def get_summary(self) -> dict[str, int]:
        return self._task_service.get_summary()

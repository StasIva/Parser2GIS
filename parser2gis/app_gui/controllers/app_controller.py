from __future__ import annotations

from typing import Any, Callable

from parser2gis.storage.repositories.city_repo import CityRepo
from parser2gis.storage.repositories.rubric_repo import RubricRepo
from parser2gis.storage.repositories.task_repo import TaskRepo


class AppController:
    def __init__(self) -> None:
        self._on_tasks_changed: Callable[[], None] | None = None
        self._on_progress: Callable[[int, int, int], None] | None = None

    def set_on_tasks_changed(self, callback: Callable[[], None]) -> None:
        self._on_tasks_changed = callback

    def get_tasks(self) -> list[dict[str, Any]]:
        return TaskRepo.get_all()

    def get_cities(self) -> list[dict[str, Any]]:
        return CityRepo.get_all()

    def get_rubrics_tree(self) -> list[dict[str, Any]]:
        return RubricRepo.find_tree()

    def create_task(self, name: str, city_id: int, rubric_id: int) -> dict[str, Any]:
        task = TaskRepo.create(name, city_id, rubric_id)
        if self._on_tasks_changed:
            self._on_tasks_changed()
        return task

    def start_task(self, task_id: int) -> None:
        TaskRepo.update_status(task_id, "running")
        if self._on_tasks_changed:
            self._on_tasks_changed()

    def pause_task(self, task_id: int) -> None:
        TaskRepo.update_status(task_id, "paused")
        if self._on_tasks_changed:
            self._on_tasks_changed()

    def stop_task(self, task_id: int) -> None:
        TaskRepo.update_status(task_id, "done")
        if self._on_tasks_changed:
            self._on_tasks_changed()

    def get_summary(self) -> dict[str, int]:
        return TaskRepo.get_summary()
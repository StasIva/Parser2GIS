from __future__ import annotations

from typing import Any

from parser2gis.domain.models import Task
from parser2gis.storage.connection import ConnectionManager
from parser2gis.storage.repositories.task_repo import TaskRepo


class TaskService:
    def create(self, name: str, city_id: int, rubric_id: int) -> Task:
        data = TaskRepo.create(name, city_id, rubric_id)
        return Task.from_dict(data)

    def get_by_id(self, task_id: int) -> Task | None:
        data = TaskRepo.get_by_id(task_id)
        return Task.from_dict(data) if data else None

    def get_all(self) -> list[Task]:
        return [Task.from_dict(d) for d in TaskRepo.get_all()]

    def update_status(self, task_id: int, status: str) -> Task:
        data = TaskRepo.update_status(task_id, status)
        return Task.from_dict(data)

    def update_progress(
        self, task_id: int, progress: int,
        orgs_found: int | None = None,
        orgs_saved: int | None = None,
        errors_count: int | None = None,
    ) -> Task | None:
        data = TaskRepo.update_progress(task_id, progress, orgs_found, orgs_saved, errors_count)
        return Task.from_dict(data) if data else None

    def update_checkpoint(self, task_id: int, checkpoint_data: str) -> None:
        TaskRepo.update_checkpoint(task_id, checkpoint_data)
        ConnectionManager.commit()

    def find_by_status(self, status: str) -> list[Task]:
        return [Task.from_dict(d) for d in TaskRepo.find_by_status(status)]

    def find_by_city_rubric(self, city_id: int, rubric_id: int) -> list[Task]:
        return [Task.from_dict(d) for d in TaskRepo.find_by_city_rubric(city_id, rubric_id)]

    def get_summary(self) -> dict[str, int]:
        return TaskRepo.get_summary()

    def delete_by_id(self, record_id: int) -> bool:
        result = TaskRepo.delete_by_id(record_id)
        return result

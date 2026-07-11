from __future__ import annotations

from typing import Any, Callable

from parser2gis.domain.models import Task
from parser2gis.services.task_service import TaskService
from parser2gis.services.organization_service import OrganizationService
from parser2gis.source_2gis.city_resolver import CityResolver
from parser2gis.source_2gis.http_client import HttpClient
from parser2gis.source_2gis.org_fetcher import OrgFetcher
from parser2gis.source_2gis.rubric_resolver import RubricResolver
from parser2gis.task_manager.models import TaskStatus
from parser2gis.task_manager.queue import TaskQueue


class TaskManager:
    def __init__(self, http_client: HttpClient, city_resolver: CityResolver,
                 rubric_resolver: RubricResolver, org_fetcher: OrgFetcher,
                 max_concurrent: int = 3) -> None:
        self._http_client = http_client
        self._city_resolver = city_resolver
        self._rubric_resolver = rubric_resolver
        self._org_fetcher = org_fetcher
        self._queue = TaskQueue(max_concurrent=max_concurrent)
        self._task_service = TaskService()
        self._org_service = OrganizationService()
        self._on_progress: Callable[[Task], None] | None = None

    def set_on_progress(self, callback: Callable[[Task], None]) -> None:
        self._on_progress = callback

    def create_task(self, name: str, city_id: int, rubric_id: int) -> Task:
        return self._task_service.create(name, city_id, rubric_id)

    def start_task(self, task_id: int) -> None:
        task = self._task_service.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        if not TaskStatus.can_transition(task.status, TaskStatus.RUNNING):
            raise ValueError(f"Cannot start task {task_id} from status {task.status}")

        self._task_service.update_status(task_id, TaskStatus.RUNNING)
        self._queue.enqueue(task)
        self._queue.start(self._run_task)

    def _run_task(self, task: Task) -> None:
        task_data = self._task_service.get_by_id(task.id)
        if not task_data:
            return
        city_id = task_data.city_id
        rubric_id = task_data.rubric_id

        orgs = self._org_fetcher.fetch_all(
            str(task.city_id),
            str(task.rubric_id),
            on_progress=lambda found, total: self._update_progress(task.id, found, total),
        )

        saved = 0
        for org in orgs:
            self._org_service.create(
                task_id=task.id,
                name=org.get("name", ""),
                source_id=str(org.get("id", "")),
                city=org.get("city", ""),
                address=org.get("address", ""),
                phones=org.get("phone", ""),
                rubric_name=org.get("rubric_name", ""),
            )
            saved += 1

        self._task_service.update_progress(task.id, 100, orgs_saved=saved)

    def _update_progress(self, task_id: int, found: int, total: int) -> None:
        pct = min(100, int((found / max(total, 1)) * 100))
        self._task_service.update_progress(task_id, pct, orgs_found=found)

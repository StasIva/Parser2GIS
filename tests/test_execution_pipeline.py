from __future__ import annotations

import os
import tempfile
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from parser2gis.domain.models import Task
from parser2gis.services.city_service import CityService
from parser2gis.services.organization_service import OrganizationService
from parser2gis.services.rubric_service import RubricService
from parser2gis.services.task_service import TaskService
from parser2gis.source_2gis.city_resolver import CityResolver
from parser2gis.source_2gis.http_client import HttpClient
from parser2gis.source_2gis.org_fetcher import OrgFetcher
from parser2gis.source_2gis.rubric_resolver import RubricResolver
from parser2gis.storage.connection import ConnectionManager
from parser2gis.storage.migration import migrate
from parser2gis.storage.repositories.city_repo import CityRepo
from parser2gis.storage.repositories.rubric_repo import RubricRepo
from parser2gis.storage.repositories.seed import seed
from parser2gis.task_manager.manager import TaskManager
from parser2gis.task_manager.models import TaskStatus
from parser2gis.task_manager.queue import TaskQueue


@pytest.fixture(autouse=True)
def _db() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        ConnectionManager.configure(db_path)
        migrate()
        seed()
        ConnectionManager.commit()
        yield
        ConnectionManager.close_all()


class TestTaskQueue:
    def test_enqueue_dequeue(self) -> None:
        q = TaskQueue(max_concurrent=1)
        task = Task(id=1, name="t1", city_id=1, rubric_id=1)
        q.enqueue(task)
        assert q.queued_count == 1
        dequeued = q.dequeue()
        assert dequeued is not None
        assert dequeued.id == 1
        assert q.queued_count == 0

    def test_dequeue_empty(self) -> None:
        q = TaskQueue(max_concurrent=1)
        assert q.dequeue() is None

    def test_running_count(self) -> None:
        q = TaskQueue(max_concurrent=2)

        results: list[int] = []
        lock = threading.Lock()

        def worker(task: Task) -> None:
            with lock:
                results.append(task.id)
            time.sleep(0.2)

        t1 = Task(id=1, name="t1", city_id=1, rubric_id=1)
        t2 = Task(id=2, name="t2", city_id=1, rubric_id=1)

        q.enqueue(t1)
        q.enqueue(t2)
        q.start(worker)

        time.sleep(0.1)
        assert q.running_count == 2

        q.stop()

    def test_queued_count(self) -> None:
        q = TaskQueue(max_concurrent=1)
        t1 = Task(id=1, name="t1", city_id=1, rubric_id=1)
        t2 = Task(id=2, name="t2", city_id=1, rubric_id=1)
        q.enqueue(t1)
        q.enqueue(t2)
        assert q.queued_count == 2

    def test_stop_clears(self) -> None:
        q = TaskQueue(max_concurrent=1)

        called = False

        def worker(task: Task) -> None:
            nonlocal called
            called = True

        t1 = Task(id=1, name="t1", city_id=1, rubric_id=1)
        q.enqueue(t1)
        q.start(worker)
        q.stop()
        time.sleep(0.05)

    def test_concurrent_limit(self) -> None:
        q = TaskQueue(max_concurrent=2)

        running_log: list[int] = []
        lock = threading.Lock()

        def worker(task: Task) -> None:
            with lock:
                running_log.append(task.id)
            time.sleep(0.3)
            with lock:
                running_log.remove(task.id)

        for i in range(5):
            q.enqueue(Task(id=i + 1, name=f"t{i+1}", city_id=1, rubric_id=1))

        q.start(worker)
        time.sleep(0.1)
        assert q.running_count == 2
        q.stop()


class TestTaskManagerLifecycle:
    def _make_task_manager(self) -> TaskManager:
        client = HttpClient(delay_ms=0)
        return TaskManager(
            client,
            CityResolver(client, api_key=""),
            RubricResolver(client, api_key=""),
            OrgFetcher(client, api_key=""),
            max_concurrent=3,
        )

    def _get_seeded_city_id(self) -> int:
        city = CityRepo.find_by_name("Москва")
        assert city is not None
        return city["id"]

    def _get_seeded_rubric_id(self) -> int:
        rubric = RubricRepo.find_by_name("Автосервис")
        assert rubric is not None
        return rubric["id"]

    def test_start_task_creates_running_status(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()
        task = tm.create_task("test", city_id, rubric_id)
        assert task.status == TaskStatus.CREATED

        tm.start_task(task.id)
        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.RUNNING

        tm._queue.stop()

    def test_start_task_invalid_id_raises(self) -> None:
        tm = self._make_task_manager()
        with pytest.raises(ValueError, match="not found"):
            tm.start_task(99999)

    def test_start_task_invalid_transition_raises(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()
        task = tm.create_task("test", city_id, rubric_id)
        TaskService().update_status(task.id, TaskStatus.DONE)
        with pytest.raises(ValueError, match="Cannot start"):
            tm.start_task(task.id)

    def test_run_task_success_lifecycle(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()
        task = tm.create_task("run-test", city_id, rubric_id)

        progress_events: list[tuple[int, int, str]] = []
        tm.set_on_progress(lambda t: progress_events.append((t.id, t.progress, t.status)))

        mock_orgs = [
            {"name": "Org1", "id": "src_1", "city": "Moscow", "address": "Addr 1",
             "phones": "+7-111", "rubric_name": "Auto"},
            {"name": "Org2", "id": "src_2", "city": "Moscow", "address": "Addr 2",
             "phones": "+7-222", "rubric_name": "Auto"},
        ]

        def mock_fetch_all(city_id, rubric_id, on_progress=None):
            if on_progress:
                on_progress(len(mock_orgs), len(mock_orgs))
            return mock_orgs

        with patch.object(tm._org_fetcher, "fetch_all", side_effect=mock_fetch_all):
            tm._run_task(task)

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.DONE
        assert updated.progress == 100
        assert updated.orgs_saved == 2

        orgs = OrganizationService().find_by_task_id(task.id)
        assert len(orgs) == 2
        assert orgs[0].name == "Org1"
        assert orgs[1].name == "Org2"

        assert len(progress_events) >= 1
        last_event = progress_events[-1]
        assert last_event[0] == task.id
        assert last_event[1] == 100
        assert last_event[2] == TaskStatus.DONE

    def test_run_task_ghost_task_returns_quietly(self) -> None:
        tm = self._make_task_manager()
        task = Task(id=99999, name="ghost", city_id=1, rubric_id=1)
        tm._run_task(task)
        updated = TaskService().get_by_id(99999)
        assert updated is None

    def test_run_task_missing_city_sets_error(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()
        task = tm.create_task("missing-city", city_id, rubric_id)

        with patch.object(tm._city_service, "get_by_id", return_value=None):
            tm._run_task(task)

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.ERROR

    def test_run_task_missing_rubric_sets_error(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()
        task = tm.create_task("missing-rubric", city_id, rubric_id)

        with patch.object(tm._rubric_service, "get_by_id", return_value=None):
            tm._run_task(task)

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.ERROR

    def test_run_task_exception_sets_error(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()
        task = tm.create_task("exception-test", city_id, rubric_id)

        with patch.object(
            tm._org_fetcher, "fetch_all", side_effect=RuntimeError("API failure")
        ):
            tm._run_task(task)

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.ERROR
        assert updated.progress == 0

    def test_run_task_progress_during_fetch(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()
        task = tm.create_task("progress-test", city_id, rubric_id)

        progress_events: list[tuple[int, int, str]] = []
        tm.set_on_progress(lambda t: progress_events.append((t.id, t.progress, t.status)))

        def fetch_with_progress(
            city_id: str, rubric_id: str,
            on_progress=None,
        ) -> list[dict]:
            if on_progress:
                on_progress(5, 100)
            return [{"name": "Org1", "id": "src_1"}]

        with patch.object(tm._org_fetcher, "fetch_all", side_effect=fetch_with_progress):
            tm._run_task(task)

        assert len(progress_events) >= 1

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.DONE

    def test_run_task_uses_source_id_when_available(self) -> None:
        tm = self._make_task_manager()

        city = CityService().upsert("TestCity", source_id="2gis_city_123")
        rubric = RubricService().upsert("TestRubric", source_id="2gis_rubric_456")
        task = tm.create_task("source-id-test", city.id, rubric.id)

        mock_orgs = [{"name": "Org1", "id": "src_1"}]

        def mock_fetch_all(city_id, rubric_id, on_progress=None):
            if on_progress:
                on_progress(1, 1)
            return mock_orgs

        with patch.object(tm._org_fetcher, "fetch_all", side_effect=mock_fetch_all) as mock_fetch:
            tm._run_task(task)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]
        assert call_args[0] == "2gis_city_123"
        assert call_args[1] == "2gis_rubric_456"

    def test_run_task_falls_back_to_local_id(self) -> None:
        tm = self._make_task_manager()
        city_id = self._get_seeded_city_id()
        rubric_id = self._get_seeded_rubric_id()

        city = CityService().get_by_id(city_id)
        rubric = RubricService().get_by_id(rubric_id)
        assert city is not None and rubric is not None
        assert city.source_id is None
        assert rubric.source_id is None

        task = tm.create_task("fallback-test", city_id, rubric_id)
        mock_orgs = [{"name": "Org1", "id": "src_1"}]

        def mock_fetch_all(city_id, rubric_id, on_progress=None):
            if on_progress:
                on_progress(1, 1)
            return mock_orgs

        with patch.object(tm._org_fetcher, "fetch_all", side_effect=mock_fetch_all) as mock_fetch:
            tm._run_task(task)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]
        assert call_args[0] == str(city_id)
        assert call_args[1] == str(rubric_id)


class TestTaskManagerIntegration:
    def _setup(self) -> tuple[TaskManager, int, int]:
        client = HttpClient(delay_ms=0)
        tm = TaskManager(
            client,
            CityResolver(client, api_key=""),
            RubricResolver(client, api_key=""),
            OrgFetcher(client, api_key=""),
            max_concurrent=3,
        )
        city = CityRepo.find_by_name("Москва")
        rubric = RubricRepo.find_by_name("Автосервис")
        assert city is not None and rubric is not None
        return tm, city["id"], rubric["id"]

    def test_full_start_execution_with_queue(self) -> None:
        tm, city_id, rubric_id = self._setup()

        progress_events: list[tuple[int, int, str]] = []
        tm.set_on_progress(lambda t: progress_events.append((t.id, t.progress, t.status)))

        task = tm.create_task("integration-test", city_id, rubric_id)
        assert task.status == TaskStatus.CREATED

        mock_orgs = [
            {"name": "Org1", "id": "src_1", "city": "Moscow", "address": "A1",
             "phones": "+7-111", "rubric_name": "Auto"},
        ]

        def mock_fetch_all(city_id, rubric_id, on_progress=None):
            if on_progress:
                on_progress(1, 1)
            return mock_orgs

        with patch.object(tm._org_fetcher, "fetch_all", side_effect=mock_fetch_all):
            tm.start_task(task.id)
            time.sleep(0.3)

        tm._queue.stop()
        time.sleep(0.05)

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.DONE
        assert updated.progress == 100

        orgs = OrganizationService().find_by_task_id(task.id)
        assert len(orgs) == 1

        assert len(progress_events) >= 1

    def test_start_task_error_in_queue_sets_error(self) -> None:
        tm, city_id, rubric_id = self._setup()

        task = tm.create_task("error-integration", city_id, rubric_id)
        assert task.status == TaskStatus.CREATED

        with patch.object(
            tm._org_fetcher, "fetch_all", side_effect=RuntimeError("Network error")
        ):
            tm.start_task(task.id)
            time.sleep(0.3)

        tm._queue.stop()
        time.sleep(0.05)

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.ERROR


class TestAppControllerWiring:
    def test_app_controller_start_task(self) -> None:
        from parser2gis.app_gui.controllers.app_controller import AppController

        client = HttpClient(delay_ms=0)
        tm = TaskManager(
            client,
            CityResolver(client, api_key=""),
            RubricResolver(client, api_key=""),
            OrgFetcher(client, api_key=""),
            max_concurrent=3,
        )
        controller = AppController(task_manager=tm)

        changed_flags: list[bool] = []
        controller.set_on_tasks_changed(lambda: changed_flags.append(True))

        city_id = CityRepo.find_by_name("Москва")["id"]
        rubric_id = RubricRepo.find_by_name("Автосервис")["id"]
        task_dict = controller.create_task("app-test", city_id, rubric_id)
        assert len(changed_flags) >= 1

        task = TaskService().get_by_id(task_dict["id"])
        assert task is not None
        assert task.status == TaskStatus.CREATED

        mock_orgs = [{"name": "Org1", "id": "src_1"}]

        def mock_fetch_all(city_id, rubric_id, on_progress=None):
            if on_progress:
                on_progress(1, 1)
            return mock_orgs

        with patch.object(tm._org_fetcher, "fetch_all", side_effect=mock_fetch_all):
            controller.start_task(task.id)
            time.sleep(0.3)

        tm._queue.stop()
        time.sleep(0.05)

        updated = TaskService().get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.DONE

    def test_controller_progress_callback(self) -> None:
        from parser2gis.app_gui.controllers.app_controller import AppController

        client = HttpClient(delay_ms=0)
        tm = TaskManager(
            client,
            CityResolver(client, api_key=""),
            RubricResolver(client, api_key=""),
            OrgFetcher(client, api_key=""),
            max_concurrent=3,
        )
        controller = AppController(task_manager=tm)

        progress_events: list[tuple[int, int, str]] = []
        controller.set_on_progress(
            lambda task_id, progress, status: progress_events.append(
                (task_id, progress, status)
            )
        )

        city_id = CityRepo.find_by_name("Москва")["id"]
        rubric_id = RubricRepo.find_by_name("Автосервис")["id"]
        task = tm.create_task("progress-cb", city_id, rubric_id)

        def fetch_with_cb(city_id, rubric_id, on_progress=None):
            if on_progress:
                on_progress(3, 10)
            return [{"name": "Org1", "id": "src_1"}]

        with patch.object(tm._org_fetcher, "fetch_all", side_effect=fetch_with_cb):
            controller.start_task(task.id)
            time.sleep(0.3)

        tm._queue.stop()
        time.sleep(0.05)

        assert len(progress_events) >= 1
        last = progress_events[-1]
        assert last[0] == task.id
        assert last[1] == 100

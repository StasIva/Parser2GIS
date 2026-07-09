from __future__ import annotations

import os
import tempfile

import pytest

from parser2gis.storage.connection import ConnectionManager
from parser2gis.storage.migration import migrate
from parser2gis.storage.repositories.city_repo import CityRepo
from parser2gis.storage.repositories.rubric_repo import RubricRepo
from parser2gis.storage.repositories.organization_repo import OrganizationRepo
from parser2gis.storage.repositories.task_repo import TaskRepo
from parser2gis.storage.repositories.contact_repo import ContactRepo
from parser2gis.storage.repositories.export_repo import ExportRepo
from parser2gis.storage.repositories.parse_log_repo import ParseLogRepo
from parser2gis.storage.repositories.seed import seed


@pytest.fixture(autouse=True)
def _db() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        ConnectionManager.configure(db_path)
        migrate()
        seed()
        # Ensure a valid task exists for FK-referencing tests
        city = CityRepo.find_by_name("Москва")
        rubric = RubricRepo.find_by_name("Автосервис")
        if city and rubric:
            TaskRepo.create("Test Task", city_id=city["id"], rubric_id=rubric["id"])
        yield
        ConnectionManager.close_all()


class TestCityRepo:
    def test_create_and_find(self) -> None:
        city = CityRepo.create("Тестовый", source_id="test_1", region="Тест")
        assert city["name"] == "Тестовый"
        assert city["source_id"] == "test_1"

        found = CityRepo.find_by_name("Тестовый")
        assert found is not None
        assert found["id"] == city["id"]

    def test_find_by_source_id(self) -> None:
        city = CityRepo.create("Test", source_id="src_123")
        found = CityRepo.find_by_source_id("src_123")
        assert found is not None
        assert found["id"] == city["id"]

    def test_upsert_new(self) -> None:
        city = CityRepo.upsert("Новый", source_id="new_id", region="Область")
        assert city["name"] == "Новый"

    def test_upsert_existing(self) -> None:
        city = CityRepo.create("Existing", source_id="old_id")
        updated = CityRepo.upsert("Existing", source_id="new_id")
        assert updated["id"] == city["id"]
        assert updated["source_id"] == "new_id"

    def test_seed_data_exists(self) -> None:
        cities = CityRepo.get_all()
        names = {c["name"] for c in cities}
        assert "Москва" in names
        assert "Санкт-Петербург" in names
        assert "Новосибирск" in names

    def test_count(self) -> None:
        assert CityRepo.count() >= 3

    def test_exists(self) -> None:
        city = CityRepo.find_by_name("Москва")
        if city:
            assert CityRepo.exists(city["id"]) is True
        assert CityRepo.exists(99999) is False

    def test_get_by_id(self) -> None:
        city = CityRepo.find_by_name("Москва")
        if city:
            same = CityRepo.get_by_id(city["id"])
            assert same is not None
            assert same["name"] == "Москва"

    def test_delete_by_id(self) -> None:
        city = CityRepo.create("ToDelete")
        assert CityRepo.delete_by_id(city["id"]) is True
        assert CityRepo.get_by_id(city["id"]) is None


class TestRubricRepo:
    def test_create_and_find_tree(self) -> None:
        parent = RubricRepo.create("Категория", sort_order=1)
        child = RubricRepo.create("Подкатегория", parent_id=parent["id"], sort_order=2)
        tree = RubricRepo.find_tree()
        names = {r["name"] for r in tree}
        assert parent["name"] in names

    def test_find_children(self) -> None:
        parent = RubricRepo.create("Parent", sort_order=1)
        child = RubricRepo.create("Child", parent_id=parent["id"], sort_order=2)
        children = RubricRepo.find_children(parent["id"])
        assert len(children) == 1
        assert children[0]["name"] == "Child"

    def test_seed_data_rubrics_exist(self) -> None:
        rubrics = RubricRepo.get_all()
        names = {r["name"] for r in rubrics}
        assert "Автосервис" in names
        assert "Рестораны" in names


class TestOrganizationRepo:
    @property
    def _tid(self) -> int:
        tasks = TaskRepo.get_all()
        return tasks[0]["id"] if tasks else 1

    def test_create_and_find_by_task(self) -> None:
        tid = self._tid
        org = OrganizationRepo.create(task_id=tid, name="Test Org")
        assert org["name"] == "Test Org"
        orgs = OrganizationRepo.find_by_task_id(tid)
        assert len(orgs) == 1

    def test_dedup_by_source_id(self) -> None:
        tid = self._tid
        OrganizationRepo.create(task_id=tid, name="Org1", source_id="src_1")
        dup = OrganizationRepo.dedup_by_source_id(tid, "src_1")
        assert dup is not None
        no_dup = OrganizationRepo.dedup_by_source_id(tid, "src_2")
        assert no_dup is None

    def test_get_page(self) -> None:
        tid = self._tid
        for i in range(5):
            OrganizationRepo.create(task_id=tid, name=f"Org{i}")
        page = OrganizationRepo.get_page(tid, offset=0, limit=3)
        assert len(page) == 3
        page2 = OrganizationRepo.get_page(tid, offset=3, limit=3)
        assert len(page2) == 2


class TestTaskRepo:
    @property
    def _cid(self) -> int:
        city = CityRepo.find_by_name("Москва")
        return city["id"] if city else 1

    @property
    def _rid(self) -> int:
        rubric = RubricRepo.find_by_name("Автосервис")
        return rubric["id"] if rubric else 1

    def test_create_and_update_status(self) -> None:
        task = TaskRepo.create("Test Task", city_id=self._cid, rubric_id=self._rid)
        assert task["status"] == "created"
        updated = TaskRepo.update_status(task["id"], "running")
        assert updated["status"] == "running"

    def test_update_progress(self) -> None:
        task = TaskRepo.create("Progress", city_id=self._cid, rubric_id=self._rid)
        updated = TaskRepo.update_progress(task["id"], 50, orgs_found=10, orgs_saved=5)
        assert updated["progress"] == 50
        assert updated["orgs_found"] == 10

    def test_find_by_status(self) -> None:
        t1 = TaskRepo.create("T1", city_id=self._cid, rubric_id=self._rid)
        TaskRepo.update_status(t1["id"], "running")
        running = TaskRepo.find_by_status("running")
        assert len(running) >= 1
        assert running[0]["id"] == t1["id"]

    def test_get_summary(self) -> None:
        summary = TaskRepo.get_summary()
        assert "created" in summary
        assert "running" in summary

    def test_update_checkpoint(self) -> None:
        task = TaskRepo.create("Check", city_id=self._cid, rubric_id=self._rid)
        TaskRepo.update_checkpoint(task["id"], '{"page": 3}')
        reloaded = TaskRepo.get_by_id(task["id"])
        assert reloaded["checkpoint_data"] == '{"page": 3}'

    def test_invalid_status_raises(self) -> None:
        task = TaskRepo.create("Bad", city_id=self._cid, rubric_id=self._rid)
        with pytest.raises(ValueError):
            TaskRepo.update_status(task["id"], "invalid")


class TestContactRepo:
    @property
    def _oid(self) -> int:
        tid = TestOrganizationRepo()._tid
        org = OrganizationRepo.create(task_id=tid, name="OrgForContacts")
        return org["id"]

    def test_create_and_find(self) -> None:
        oid = self._oid
        contact = ContactRepo.create(organization_id=oid, type_="phone", value="+71234567890")
        assert contact["type"] == "phone"
        assert contact["value"] == "+71234567890"

    def test_find_by_organization(self) -> None:
        oid = self._oid
        ContactRepo.create(organization_id=oid, type_="email", value="test@example.com")
        contacts = ContactRepo.find_by_organization(oid)
        assert len(contacts) == 1
        assert contacts[0]["value"] == "test@example.com"

    def test_delete_by_organization(self) -> None:
        oid = self._oid
        ContactRepo.create(organization_id=oid, type_="phone", value="+7111")
        ContactRepo.create(organization_id=oid, type_="email", value="a@b.com")
        deleted = ContactRepo.delete_by_organization(oid)
        assert deleted == 2
        assert ContactRepo.find_by_organization(oid) == []


class TestExportRepo:
    @property
    def _tid(self) -> int:
        tasks = TaskRepo.get_all()
        return tasks[0]["id"] if tasks else 1

    def test_create_and_complete(self) -> None:
        export = ExportRepo.create(task_id=self._tid, fmt="xlsx", file_path="/tmp/test.xlsx")
        assert export["status"] == "running"
        completed = ExportRepo.complete(export["id"], record_count=10)
        assert completed["status"] == "done"
        assert completed["record_count"] == 10

    def test_find_by_task(self) -> None:
        ExportRepo.create(task_id=self._tid, fmt="csv", file_path="/tmp/a.csv")
        exports = ExportRepo.find_by_task_id(self._tid)
        assert len(exports) >= 1


class TestParseLogRepo:
    @property
    def _tid(self) -> int:
        tasks = TaskRepo.get_all()
        return tasks[0]["id"] if tasks else 1

    def test_create_and_find(self) -> None:
        log = ParseLogRepo.create(task_id=self._tid, level="info", message="Started")
        assert log["message"] == "Started"
        logs = ParseLogRepo.find_by_task_id(self._tid)
        assert len(logs) == 1

    def test_find_by_level(self) -> None:
        tid = self._tid
        ParseLogRepo.create(task_id=tid, level="error", message="Error 1")
        ParseLogRepo.create(task_id=tid, level="info", message="Info 1")
        errors = ParseLogRepo.find_by_task_and_level(tid, "error")
        assert len(errors) == 1
        assert errors[0]["message"] == "Error 1"


class TestConnectionManager:
    def test_configure_and_connection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test2.db")
            ConnectionManager.configure(db_path)
            conn = ConnectionManager.connection()
            assert conn is not None

    def test_integrity_check(self) -> None:
        issues = ConnectionManager.check_integrity()
        assert issues == []

    def test_begin_commit_rollback(self) -> None:
        ConnectionManager.begin()
        assert ConnectionManager.in_transaction() is True
        ConnectionManager.commit()
        assert ConnectionManager.in_transaction() is False

    def test_db_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "t.db")
            ConnectionManager.configure(db_path)
            assert ConnectionManager.db_path() == db_path


class TestCache:
    def test_cache_basic(self) -> None:
        from parser2gis.storage.cache import MemoryCache

        cache = MemoryCache(ttl_seconds=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_cache_expiry(self) -> None:
        from parser2gis.storage.cache import MemoryCache

        cache = MemoryCache(ttl_seconds=0)
        cache.set("key", "val")
        import time
        time.sleep(0.01)
        assert cache.get("key") is None

    def test_serialization(self) -> None:
        from parser2gis.storage.cache import MemoryCache

        cache = MemoryCache(ttl_seconds=60)
        cache.set("a", 1)
        cache.set("b", "hello")
        data = cache.to_json()
        restored = MemoryCache.from_json(data)
        assert restored.get("a") == 1
        assert restored.get("b") == "hello"


class TestPhoneExtractor:
    def test_extract(self) -> None:
        from parser2gis.parser.phone_extractor import PhoneExtractor

        extractor = PhoneExtractor()
        phones = extractor.extract([{"number": "+7 (495) 123-45-67"}, "8 (812) 234-56-78"])
        assert len(phones) == 2
        assert "+74951234567" in phones
        assert "+78122345678" in phones

    def test_is_mobile(self) -> None:
        from parser2gis.parser.phone_extractor import PhoneExtractor

        extractor = PhoneExtractor()
        assert extractor.is_mobile("+79161234567") is True
        assert extractor.is_mobile("+74951234567") is False


class TestAddressNormalizer:
    def test_normalize(self) -> None:
        from parser2gis.parser.address_normalizer import AddressNormalizer

        n = AddressNormalizer()
        assert n.normalize("  ул.  Ленина,  д. 10  ") == "ул. Ленина, д. 10"

    def test_split(self) -> None:
        from parser2gis.parser.address_normalizer import AddressNormalizer

        n = AddressNormalizer()
        parts = n.split("Москва, ул. Тверская, д. 15")
        assert parts["city"] == "Москва"
        assert parts["street"] == "ул. Тверская"
        assert parts["building"] == "15"


class TestOrganizationParser:
    def test_parse_minimal(self) -> None:
        from parser2gis.parser.organization_parser import OrganizationParser

        parser = OrganizationParser()
        result = parser.parse({"name": "Test Org", "id": "123"})
        assert result["name"] == "Test Org"
        assert result["source_id"] == "123"

    def test_parse_full(self) -> None:
        from parser2gis.parser.organization_parser import OrganizationParser

        parser = OrganizationParser()
        raw = {
            "id": "org_1",
            "name": "  ООО Ромашка  ",
            "address_name": "Москва, ул. Ленина, 1",
            "phones": [{"number": "+7 (495) 123-45-67"}],
            "emails": ["info@romashka.ru"],
            "sites": [{"url": "https://romashka.ru"}],
            "rubrics": [{"name": "Автосервис"}],
            "working_hours": {"пн-пт": "09:00-18:00"},
            "point": {"lat": 55.75, "lon": 37.62},
        }
        parsed = parser.parse(raw)
        assert parsed["name"] == "ООО Ромашка"
        assert parsed["source_id"] == "org_1"
        assert parsed["phones"] != ""
        assert parsed["emails"] == "info@romashka.ru"
        assert parsed["website"] == "https://romashka.ru"
        assert parsed["lat"] == 55.75
        assert parsed["lon"] == 37.62


class TestDeduplicator:
    def test_find_duplicates(self) -> None:
        from parser2gis.parser.deduplicator import Deduplicator

        d = Deduplicator()
        orgs = [
            {"id": 1, "source_id": "a", "name": "X", "address": "Addr1"},
            {"id": 2, "source_id": "b", "name": "Y", "address": "Addr2"},
            {"id": 3, "source_id": "a", "name": "X", "address": "Addr1"},
        ]
        dups = d.find_duplicates(1, orgs)
        assert dups == [3]


class TestExporter:
    def test_xlsx_export(self) -> None:
        from parser2gis.exporter.xlsx_exporter import XlsxExporter

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.xlsx")
            records = [
                {"id": 1, "name": "Test", "city": "Msk", "address": "Addr",
                 "phones": "+7123", "emails": "a@b.com", "website": "http://x.ru",
                 "rubric_name": "Auto", "work_hours": "9-18", "lat": 55.0, "lon": 37.0, "source_id": "src1"},
            ]
            result = XlsxExporter().export(records, path)
            assert os.path.isfile(result)

    def test_csv_export(self) -> None:
        from parser2gis.exporter.csv_exporter import CsvExporter

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.csv")
            records = [{"id": 1, "name": "Test"}]
            result = CsvExporter().export(records, path)
            assert os.path.isfile(result)

    def test_json_export(self) -> None:
        from parser2gis.exporter.json_exporter import JsonExporter

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.json")
            records = [{"id": 1, "name": "Test"}]
            result = JsonExporter().export(records, path)
            assert os.path.isfile(result)


class TestTaskManagerModels:
    def test_task_status_transitions(self) -> None:
        from parser2gis.task_manager.models import TaskStatus

        assert TaskStatus.can_transition("created", "running") is True
        assert TaskStatus.can_transition("running", "paused") is True
        assert TaskStatus.can_transition("done", "running") is False
        assert TaskStatus.can_transition("error", "created") is True

    def test_task_info_from_dict(self) -> None:
        from parser2gis.task_manager.models import TaskInfo

        info = TaskInfo.from_dict({
            "id": 1, "name": "Test", "city_id": 1, "rubric_id": 1,
            "status": "created",
        })
        assert info.id == 1
        assert info.name == "Test"
        assert info.status == "created"


class TestCrashRecovery:
    def test_checkpoint_round_trip(self) -> None:
        from parser2gis.task_manager.recovery import CrashRecovery
        from parser2gis.storage.repositories.task_repo import TaskRepo

        # Valid city/rubric from seed
        city = CityRepo.find_by_name("Москва")
        rubric = RubricRepo.find_by_name("Автосервис")
        assert city and rubric

        task = TaskRepo.create("Recovery", city_id=city["id"], rubric_id=rubric["id"])
        TaskRepo.update_status(task["id"], "running")
        CrashRecovery.save_checkpoint(task["id"], {"page": 2, "processed": 10})
        checkpoint = CrashRecovery.resume_task(task["id"])
        assert checkpoint is not None
        assert checkpoint["page"] == 2
        assert checkpoint["processed"] == 10
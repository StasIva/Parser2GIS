from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from parser2gis.services.directory_update_service import (
    DirectoryUpdateResult,
    DirectoryUpdateService,
)
from parser2gis.source_2gis.city_resolver import CityResolver
from parser2gis.source_2gis.rubric_resolver import RubricResolver


@pytest.fixture
def mock_city_service() -> MagicMock:
    svc = MagicMock()
    svc.find_by_name.return_value = None
    svc.upsert.return_value = MagicMock(to_dict=lambda: {"id": 1, "name": "MockCity"})
    return svc


@pytest.fixture
def mock_rubric_service() -> MagicMock:
    svc = MagicMock()
    svc.find_by_name.return_value = None
    svc.upsert.return_value = MagicMock(to_dict=lambda: {"id": 1, "name": "MockRubric"})
    return svc


@pytest.fixture
def service(mock_city_service: MagicMock, mock_rubric_service: MagicMock) -> DirectoryUpdateService:
    svc = DirectoryUpdateService.__new__(DirectoryUpdateService)
    svc._client = MagicMock()
    svc._city_resolver = MagicMock(spec=CityResolver)
    svc._rubric_resolver = MagicMock(spec=RubricResolver)
    svc._city_service = mock_city_service
    svc._rubric_service = mock_rubric_service
    return svc


class TestDirectoryUpdateResult:
    def test_defaults(self) -> None:
        r = DirectoryUpdateResult(0, 0, 0, 0, 0, 0, [])
        assert r.total_cities == 0
        assert r.total_rubrics == 0

    def test_totals(self) -> None:
        r = DirectoryUpdateResult(10, 3, 1, 20, 5, 2, [])
        assert r.total_cities == 4
        assert r.total_rubrics == 7

    def test_to_dict(self) -> None:
        r = DirectoryUpdateResult(10, 3, 1, 20, 5, 2, ["err"])
        d = r.to_dict()
        assert d["cities_found"] == 10
        assert d["cities_added"] == 3
        assert d["cities_updated"] == 1
        assert d["rubrics_found"] == 20
        assert d["rubrics_added"] == 5
        assert d["rubrics_updated"] == 2
        assert d["errors"] == ["err"]


class TestDirectoryUpdateService:
    def test_update_cities_adds_new(self, service: DirectoryUpdateService) -> None:
        service._city_resolver.search.return_value = [
            {"name": "Москва", "id": "city_1", "region": "Московская обл."},
        ]
        service._city_service.find_by_name.return_value = None

        result = service.update_cities(["Москва"])
        assert result.cities_found == 1
        assert result.cities_added == 1
        assert result.cities_updated == 0
        service._city_service.upsert.assert_called_once_with(
            "Москва", "city_1", "Московская обл."
        )

    def test_update_cities_updates_existing(self, service: DirectoryUpdateService) -> None:
        existing = MagicMock()
        existing.source_id = "old_id"
        existing.region = "Old Region"
        service._city_resolver.search.return_value = [
            {"name": "Москва", "id": "new_id", "region": "Московская обл."},
        ]
        service._city_service.find_by_name.return_value = existing

        result = service.update_cities(["Москва"])
        assert result.cities_found == 1
        assert result.cities_added == 0
        assert result.cities_updated == 1
        service._city_service.upsert.assert_called_once_with(
            "Москва", "new_id", "Московская обл."
        )

    def test_update_cities_skips_unchanged(self, service: DirectoryUpdateService) -> None:
        existing = MagicMock()
        existing.source_id = "city_1"
        existing.region = "Московская обл."
        service._city_resolver.search.return_value = [
            {"name": "Москва", "id": "city_1", "region": "Московская обл."},
        ]
        service._city_service.find_by_name.return_value = existing

        result = service.update_cities(["Москва"])
        assert result.cities_found == 1
        assert result.cities_added == 0
        assert result.cities_updated == 0
        service._city_service.upsert.assert_not_called()

    def test_update_cities_skips_empty_name(self, service: DirectoryUpdateService) -> None:
        service._city_resolver.search.return_value = [
            {"name": "", "id": "city_1", "region": "Test"},
        ]
        result = service.update_cities(["Test"])
        assert result.cities_found == 1
        assert result.cities_added == 0
        service._city_service.upsert.assert_not_called()

    def test_update_cities_empty_results(self, service: DirectoryUpdateService) -> None:
        service._city_resolver.search.return_value = []
        result = service.update_cities(["Nonexistent"])
        assert result.cities_found == 0
        assert result.cities_added == 0
        service._city_service.upsert.assert_not_called()

    def test_update_rubrics_adds_new(self, service: DirectoryUpdateService) -> None:
        service._rubric_resolver.search.return_value = [
            {"name": "Автосервис", "id": "rub_1", "parent_name": None},
        ]
        service._rubric_service.find_by_name.return_value = None

        result = service.update_rubrics(["Авто"])
        assert result.rubrics_found == 1
        assert result.rubrics_added == 1
        assert result.rubrics_updated == 0
        service._rubric_service.upsert.assert_called_once_with(
            "Автосервис", None, "rub_1", 1
        )

    def test_update_rubrics_with_parent(self, service: DirectoryUpdateService) -> None:
        parent = MagicMock()
        parent.id = 42
        service._rubric_resolver.search.return_value = [
            {"name": "Шиномонтаж", "id": "rub_2", "parent_name": "Автосервис"},
        ]

        def find_by_name_side_effect(name: str) -> MagicMock | None:
            if name == "Автосервис":
                return parent
            return None
        service._rubric_service.find_by_name.side_effect = find_by_name_side_effect

        result = service.update_rubrics(["Шиномонтаж"])
        assert result.rubrics_found == 1
        assert result.rubrics_added == 1
        service._rubric_service.upsert.assert_called_once_with(
            "Шиномонтаж", 42, "rub_2", 1
        )

    def test_update_rubrics_skips_unchanged(self, service: DirectoryUpdateService) -> None:
        existing = MagicMock()
        existing.source_id = "rub_1"
        existing.parent_id = None
        service._rubric_resolver.search.return_value = [
            {"name": "Автосервис", "id": "rub_1", "parent_name": None},
        ]
        service._rubric_service.find_by_name.return_value = existing

        result = service.update_rubrics(["Авто"])
        assert result.rubrics_found == 1
        assert result.rubrics_added == 0
        assert result.rubrics_updated == 0
        service._rubric_service.upsert.assert_not_called()

    def test_update_rubrics_empty_name(self, service: DirectoryUpdateService) -> None:
        service._rubric_resolver.search.return_value = [
            {"name": "", "id": "rub_1", "parent_name": None},
        ]
        result = service.update_rubrics(["Test"])
        assert result.rubrics_found == 1
        assert result.rubrics_added == 0
        service._rubric_service.upsert.assert_not_called()

    def test_update_all_both_succeed(self, service: DirectoryUpdateService) -> None:
        service._city_resolver.search.return_value = []
        service._rubric_resolver.search.return_value = []
        result = service.update_all()
        assert result.cities_found == 0
        assert result.rubrics_found == 0
        assert result.errors == []

    def test_update_all_city_failure(self, service: DirectoryUpdateService) -> None:
        service._city_resolver.search.side_effect = Exception("API down")
        service._rubric_resolver.search.return_value = []
        result = service.update_all()
        assert len(result.errors) == 1
        assert "API down" in result.errors[0]

    def test_update_all_rubric_failure(self, service: DirectoryUpdateService) -> None:
        service._city_resolver.search.return_value = []
        service._rubric_resolver.search.side_effect = Exception("Rubric API down")
        result = service.update_all()
        assert len(result.errors) == 1
        assert "Rubric API down" in result.errors[0]

    def test_update_all_both_fail(self, service: DirectoryUpdateService) -> None:
        service._city_resolver.search.side_effect = Exception("City error")
        service._rubric_resolver.search.side_effect = Exception("Rubric error")
        result = service.update_all()
        assert len(result.errors) == 2

    def test_close(self, service: DirectoryUpdateService) -> None:
        service.close()
        service._client.close.assert_called_once()

    def test_default_queries(self) -> None:
        from parser2gis.services.directory_update_service import (
            DEFAULT_CITY_QUERIES,
            DEFAULT_RUBRIC_QUERIES,
        )
        assert len(DEFAULT_CITY_QUERIES) >= 15
        assert len(DEFAULT_RUBRIC_QUERIES) >= 12

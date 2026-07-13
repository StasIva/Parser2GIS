from __future__ import annotations

from typing import Any

from parser2gis.services.city_service import CityService
from parser2gis.services.rubric_service import RubricService
from parser2gis.source_2gis.city_resolver import CityResolver
from parser2gis.source_2gis.http_client import HttpClient
from parser2gis.source_2gis.rubric_resolver import RubricResolver

DEFAULT_CITY_QUERIES: list[str] = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Красноярск",
    "Нижний Новгород",
    "Челябинск",
    "Уфа",
    "Самара",
    "Ростов-на-Дону",
    "Омск",
    "Воронеж",
    "Пермь",
    "Волгоград",
]

DEFAULT_RUBRIC_QUERIES: list[str] = [
    "Авто",
    "Медицина",
    "Образование",
    "Рестораны",
    "Магазины",
    "Спорт",
    "Красота",
    "Транспорт",
    "Гостиницы",
    "Культура",
    "Банки",
    "Услуги",
]


class DirectoryUpdateResult:
    def __init__(
        self,
        cities_found: int,
        cities_added: int,
        cities_updated: int,
        rubrics_found: int,
        rubrics_added: int,
        rubrics_updated: int,
        errors: list[str],
    ) -> None:
        self.cities_found = cities_found
        self.cities_added = cities_added
        self.cities_updated = cities_updated
        self.rubrics_found = rubrics_found
        self.rubrics_added = rubrics_added
        self.rubrics_updated = rubrics_updated
        self.errors = errors

    @property
    def total_cities(self) -> int:
        return self.cities_added + self.cities_updated

    @property
    def total_rubrics(self) -> int:
        return self.rubrics_added + self.rubrics_updated

    def to_dict(self) -> dict[str, Any]:
        return {
            "cities_found": self.cities_found,
            "cities_added": self.cities_added,
            "cities_updated": self.cities_updated,
            "rubrics_found": self.rubrics_found,
            "rubrics_added": self.rubrics_added,
            "rubrics_updated": self.rubrics_updated,
            "errors": self.errors,
        }


class DirectoryUpdateService:
    def __init__(self, client: HttpClient | None = None, api_key: str = "") -> None:
        self._client = client or HttpClient(delay_ms=300)
        self._city_resolver = CityResolver(self._client, api_key)
        self._rubric_resolver = RubricResolver(self._client, api_key)
        self._city_service = CityService()
        self._rubric_service = RubricService()

    def update_cities(self, queries: list[str] | None = None) -> DirectoryUpdateResult:
        queries = queries or DEFAULT_CITY_QUERIES
        found = 0
        added = 0
        updated = 0

        for query in queries:
            results = self._city_resolver.search(query)
            if not results:
                continue
            for city_data in results:
                found += 1
                name = city_data.get("name", "")
                source_id = city_data.get("id") or None
                region = city_data.get("region") or None
                if not name:
                    continue
                existing = self._city_service.find_by_name(name)
                if existing:
                    needs_update = False
                    if source_id and existing.source_id != source_id:
                        needs_update = True
                    if region and existing.region != region:
                        needs_update = True
                    if needs_update:
                        self._city_service.upsert(name, source_id, region)
                        updated += 1
                else:
                    self._city_service.upsert(name, source_id, region)
                    added += 1

        return DirectoryUpdateResult(found, added, updated, 0, 0, 0, [])

    def update_rubrics(self, queries: list[str] | None = None) -> DirectoryUpdateResult:
        queries = queries or DEFAULT_RUBRIC_QUERIES
        found = 0
        added = 0
        updated = 0

        sort_order = 0
        for query in queries:
            sort_order += 1
            results = self._rubric_resolver.search(query)
            if not results:
                continue
            for rubric_data in results:
                found += 1
                name = rubric_data.get("name", "")
                source_id = rubric_data.get("id") or None
                parent_name = rubric_data.get("parent_name")
                if not name:
                    continue
                parent_id: int | None = None
                if parent_name:
                    parent = self._rubric_service.find_by_name(parent_name)
                    if parent:
                        parent_id = parent.id

                existing = self._rubric_service.find_by_name(name)
                if existing:
                    needs_update = False
                    if source_id and existing.source_id != source_id:
                        needs_update = True
                    if parent_id is not None and existing.parent_id != parent_id:
                        needs_update = True
                    if needs_update:
                        self._rubric_service.upsert(name, parent_id, source_id, sort_order)
                        updated += 1
                else:
                    self._rubric_service.upsert(name, parent_id, source_id, sort_order)
                    added += 1

        return DirectoryUpdateResult(0, 0, 0, found, added, updated, [])

    def update_all(self) -> DirectoryUpdateResult:
        errors: list[str] = []
        cities_result = DirectoryUpdateResult(0, 0, 0, 0, 0, 0, [])
        rubrics_result = DirectoryUpdateResult(0, 0, 0, 0, 0, 0, [])

        try:
            cities_result = self.update_cities()
        except Exception as e:
            errors.append(f"City update failed: {e}")

        try:
            rubrics_result = self.update_rubrics()
        except Exception as e:
            errors.append(f"Rubric update failed: {e}")

        return DirectoryUpdateResult(
            cities_found=cities_result.cities_found,
            cities_added=cities_result.cities_added,
            cities_updated=cities_result.cities_updated,
            rubrics_found=rubrics_result.rubrics_found,
            rubrics_added=rubrics_result.rubrics_added,
            rubrics_updated=rubrics_result.rubrics_updated,
            errors=errors,
        )

    def close(self) -> None:
        self._client.close()

from __future__ import annotations

from parser2gis.domain.models import Organization
from parser2gis.storage.repositories.organization_repo import OrganizationRepo


class OrganizationService:
    def create(
        self, task_id: int, name: str, source_id: str | None = None,
        city: str | None = None, address: str | None = None,
        phones: str | None = None, emails: str | None = None,
        website: str | None = None, social: str | None = None,
        rubric_name: str | None = None, work_hours: str | None = None,
        lat: float | None = None, lon: float | None = None,
        raw_json: str | None = None,
    ) -> Organization:
        data = OrganizationRepo.create(
            task_id, name, source_id, city, address, phones, emails,
            website, social, rubric_name, work_hours, lat, lon, raw_json,
        )
        return Organization.from_dict(data)

    def find_by_source_id(self, source_id: str) -> Organization | None:
        data = OrganizationRepo.find_by_source_id(source_id)
        return Organization.from_dict(data) if data else None

    def find_by_task_id(self, task_id: int) -> list[Organization]:
        return [Organization.from_dict(d) for d in OrganizationRepo.find_by_task_id(task_id)]

    def count_by_task_id(self, task_id: int) -> int:
        return OrganizationRepo.count_by_task_id(task_id)

    def get_page(self, task_id: int, offset: int = 0, limit: int = 100) -> list[Organization]:
        return [Organization.from_dict(d) for d in OrganizationRepo.get_page(task_id, offset, limit)]

    def search(
        self, query: str, task_id: int | None = None,
        limit: int = 50, offset: int = 0,
    ) -> list[Organization]:
        return [Organization.from_dict(d) for d in OrganizationRepo.search(query, task_id, limit, offset)]

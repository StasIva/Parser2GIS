from __future__ import annotations

from parser2gis.domain.models import City
from parser2gis.storage.connection import ConnectionManager
from parser2gis.storage.repositories.city_repo import CityRepo


class CityService:
    def create(self, name: str, source_id: str | None = None, region: str | None = None) -> City:
        data = CityRepo.create(name, source_id, region)
        return City.from_dict(data)

    def find_by_name(self, name: str) -> City | None:
        data = CityRepo.find_by_name(name)
        return City.from_dict(data) if data else None

    def find_by_source_id(self, source_id: str) -> City | None:
        data = CityRepo.find_by_source_id(source_id)
        return City.from_dict(data) if data else None

    def get_by_id(self, record_id: int) -> City | None:
        data = CityRepo.get_by_id(record_id)
        return City.from_dict(data) if data else None

    def get_all(self) -> list[City]:
        return [City.from_dict(d) for d in CityRepo.get_all()]

    def upsert(self, name: str, source_id: str | None = None, region: str | None = None) -> City:
        data = CityRepo.upsert(name, source_id, region)
        ConnectionManager.commit()
        return City.from_dict(data)

    def delete_by_id(self, record_id: int) -> bool:
        result = CityRepo.delete_by_id(record_id)
        return result

    def count(self) -> int:
        return CityRepo.count()

    def exists(self, record_id: int) -> bool:
        return CityRepo.exists(record_id)

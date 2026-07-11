from __future__ import annotations

from parser2gis.domain.models import Rubric
from parser2gis.storage.connection import ConnectionManager
from parser2gis.storage.repositories.rubric_repo import RubricRepo


class RubricService:
    def create(
        self, name: str, parent_id: int | None = None,
        source_id: str | None = None, sort_order: int = 0,
    ) -> Rubric:
        data = RubricRepo.create(name, parent_id, source_id, sort_order)
        return Rubric.from_dict(data)

    def find_by_name(self, name: str) -> Rubric | None:
        data = RubricRepo.find_by_name(name)
        return Rubric.from_dict(data) if data else None

    def get_by_id(self, record_id: int) -> Rubric | None:
        data = RubricRepo.get_by_id(record_id)
        return Rubric.from_dict(data) if data else None

    def get_all(self) -> list[Rubric]:
        return [Rubric.from_dict(d) for d in RubricRepo.get_all()]

    def find_roots(self) -> list[Rubric]:
        return [Rubric.from_dict(d) for d in RubricRepo.find_roots()]

    def find_children(self, parent_id: int) -> list[Rubric]:
        return [Rubric.from_dict(d) for d in RubricRepo.find_children(parent_id)]

    def find_tree(self) -> list[Rubric]:
        roots = RubricRepo.find_roots()
        result: list[Rubric] = []
        for root_data in roots:
            children = [Rubric.from_dict(c) for c in RubricRepo.find_children(root_data["id"])]
            result.append(Rubric.from_dict(root_data, children=children))
        return result

    def upsert(
        self, name: str, parent_id: int | None = None,
        source_id: str | None = None, sort_order: int = 0,
    ) -> Rubric:
        data = RubricRepo.upsert(name, parent_id, source_id, sort_order)
        ConnectionManager.commit()
        return Rubric.from_dict(data)

    def delete_by_id(self, record_id: int) -> bool:
        result = RubricRepo.delete_by_id(record_id)
        return result

    def count(self) -> int:
        return RubricRepo.count()

    def exists(self, record_id: int) -> bool:
        return RubricRepo.exists(record_id)

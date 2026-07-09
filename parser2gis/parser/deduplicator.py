from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.organization_repo import OrganizationRepo


class Deduplicator:
    def is_duplicate(self, task_id: int, parsed: dict[str, Any]) -> bool:
        source_id = parsed.get("source_id", "")
        if source_id:
            existing = OrganizationRepo.dedup_by_source_id(task_id, source_id)
            if existing:
                return True

        name = parsed.get("name", "")
        address = parsed.get("address")
        if name:
            existing = OrganizationRepo.dedup_by_name_address(task_id, name, address)
            if existing:
                return True

        return False

    def find_duplicates(self, task_id: int, orgs: list[dict[str, Any]]) -> list[int]:
        seen: set[str] = set()
        duplicates: list[int] = []
        for org in orgs:
            source_id = org.get("source_id", "")
            name = org.get("name", "")
            address = org.get("address", "")
            key = source_id or f"{name}|{address}"
            if key in seen:
                duplicates.append(org.get("id", 0))
            else:
                seen.add(key)
        return duplicates
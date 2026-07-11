from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.base import BaseRepository


class ContactRepo(BaseRepository):
    table = "contacts"
    columns = ["id", "organization_id", "type", "value", "is_primary", "created_at"]

    @classmethod
    def create(cls, organization_id: int, type_: str, value: str,
               is_primary: bool = False) -> dict[str, Any]:
        conn = cls._conn()
        cursor = conn.execute(
            "INSERT INTO contacts (organization_id, type, value, is_primary) VALUES (?, ?, ?, ?)",
            (organization_id, type_, value, 1 if is_primary else 0),
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def find_by_organization(cls, organization_id: int) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM contacts WHERE organization_id = ? ORDER BY type, is_primary DESC",
            (organization_id,),
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def delete_by_organization(cls, organization_id: int) -> int:
        conn = cls._conn()
        cursor = conn.execute(
            "DELETE FROM contacts WHERE organization_id = ?", (organization_id,)
        )
        return cursor.rowcount
from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.base import BaseRepository


class CityRepo(BaseRepository):
    table = "cities"
    columns = ["id", "name", "source_id", "region", "created_at"]

    @classmethod
    def create(cls, name: str, source_id: str | None = None, region: str | None = None) -> dict[str, Any]:
        conn = cls._conn()
        cursor = conn.execute(
            "INSERT INTO cities (name, source_id, region) VALUES (?, ?, ?)",
            (name, source_id, region),
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def find_by_name(cls, name: str) -> dict[str, Any] | None:
        conn = cls._conn()
        row = conn.execute(
            "SELECT * FROM cities WHERE name = ?", (name,)
        ).fetchone()
        return cls._row_to_dict(row)

    @classmethod
    def find_by_source_id(cls, source_id: str) -> dict[str, Any] | None:
        conn = cls._conn()
        row = conn.execute(
            "SELECT * FROM cities WHERE source_id = ?", (source_id,)
        ).fetchone()
        return cls._row_to_dict(row)

    @classmethod
    def upsert(cls, name: str, source_id: str | None = None, region: str | None = None) -> dict[str, Any]:
        existing = cls.find_by_name(name)
        if existing:
            conn = cls._conn()
            conn.execute(
                "UPDATE cities SET source_id = ?, region = ? WHERE id = ?",
                (source_id, region, existing["id"]),
            )
            return cls.get_by_id(existing["id"])
        return cls.create(name, source_id, region)
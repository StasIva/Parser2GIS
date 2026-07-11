from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.base import BaseRepository


class RubricRepo(BaseRepository):
    table = "rubrics"
    columns = ["id", "name", "parent_id", "source_id", "sort_order", "created_at"]

    @classmethod
    def create(cls, name: str, parent_id: int | None = None,
               source_id: str | None = None, sort_order: int = 0) -> dict[str, Any]:
        conn = cls._conn()
        cursor = conn.execute(
            "INSERT INTO rubrics (name, parent_id, source_id, sort_order) VALUES (?, ?, ?, ?)",
            (name, parent_id, source_id, sort_order),
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def find_by_name(cls, name: str) -> dict[str, Any] | None:
        conn = cls._conn()
        row = conn.execute(
            "SELECT * FROM rubrics WHERE name = ?", (name,)
        ).fetchone()
        return cls._row_to_dict(row)

    @classmethod
    def find_roots(cls) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM rubrics WHERE parent_id IS NULL ORDER BY sort_order"
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def find_children(cls, parent_id: int) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM rubrics WHERE parent_id = ? ORDER BY sort_order",
            (parent_id,),
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def find_tree(cls) -> list[dict[str, Any]]:
        roots = cls.find_roots()
        result: list[dict[str, Any]] = []
        for root in roots:
            node = dict(root)
            node["children"] = cls.find_children(root["id"])
            result.append(node)
        return result

    @classmethod
    def upsert(cls, name: str, parent_id: int | None = None,
               source_id: str | None = None, sort_order: int = 0) -> dict[str, Any]:
        existing = cls.find_by_name(name)
        if existing:
            conn = cls._conn()
            conn.execute(
                "UPDATE rubrics SET parent_id = ?, source_id = ?, sort_order = ? WHERE id = ?",
                (parent_id, source_id, sort_order, existing["id"]),
            )
            return cls.get_by_id(existing["id"])
        return cls.create(name, parent_id, source_id, sort_order)
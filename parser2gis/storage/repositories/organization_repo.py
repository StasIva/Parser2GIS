from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.base import BaseRepository


class OrganizationRepo(BaseRepository):
    table = "organizations"
    columns = [
        "id", "task_id", "source_id", "name", "city", "address",
        "phones", "emails", "website", "social", "rubric_name",
        "work_hours", "lat", "lon", "raw_json", "created_at",
    ]

    @classmethod
    def create(cls, task_id: int, name: str, source_id: str | None = None,
               city: str | None = None, address: str | None = None,
               phones: str | None = None, emails: str | None = None,
               website: str | None = None, social: str | None = None,
               rubric_name: str | None = None, work_hours: str | None = None,
               lat: float | None = None, lon: float | None = None,
               raw_json: str | None = None) -> dict[str, Any]:
        conn = cls._conn()
        cursor = conn.execute(
            """INSERT INTO organizations
               (task_id, source_id, name, city, address, phones, emails,
                website, social, rubric_name, work_hours, lat, lon, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_id, source_id, name, city, address, phones, emails,
             website, social, rubric_name, work_hours, lat, lon, raw_json),
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def find_by_source_id(cls, source_id: str) -> dict[str, Any] | None:
        conn = cls._conn()
        row = conn.execute(
            "SELECT * FROM organizations WHERE source_id = ?", (source_id,)
        ).fetchone()
        return cls._row_to_dict(row)

    @classmethod
    def find_by_task_id(cls, task_id: int) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM organizations WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def count_by_task_id(cls, task_id: int) -> int:
        conn = cls._conn()
        row = conn.execute(
            "SELECT COUNT(*) FROM organizations WHERE task_id = ?", (task_id,)
        ).fetchone()
        return row[0] if row else 0

    @classmethod
    def dedup_by_source_id(cls, task_id: int, source_id: str) -> dict[str, Any] | None:
        conn = cls._conn()
        row = conn.execute(
            "SELECT * FROM organizations WHERE source_id = ? AND task_id = ?",
            (source_id, task_id),
        ).fetchone()
        return cls._row_to_dict(row)

    @classmethod
    def dedup_by_name_address(cls, task_id: int, name: str, address: str | None) -> dict[str, Any] | None:
        conn = cls._conn()
        if address:
            row = conn.execute(
                "SELECT * FROM organizations WHERE name = ? AND address = ? AND task_id = ?",
                (name, address, task_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM organizations WHERE name = ? AND address IS NULL AND task_id = ?",
                (name, task_id),
            ).fetchone()
        return cls._row_to_dict(row)

    @classmethod
    def get_page(cls, task_id: int, offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM organizations WHERE task_id = ? ORDER BY id LIMIT ? OFFSET ?",
            (task_id, limit, offset),
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def search(cls, query: str, task_id: int | None = None,
               limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        conn = cls._conn()
        if task_id is not None:
            rows = conn.execute(
                """SELECT o.* FROM organizations o
                   JOIN organizations_fts fts ON o.id = fts.rowid
                   WHERE organizations_fts MATCH ? AND o.task_id = ?
                   ORDER BY rank
                   LIMIT ? OFFSET ?""",
                (query, task_id, limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT o.* FROM organizations o
                   JOIN organizations_fts fts ON o.id = fts.rowid
                   WHERE organizations_fts MATCH ?
                   ORDER BY rank
                   LIMIT ? OFFSET ?""",
                (query, limit, offset),
            ).fetchall()
        return cls._rows_to_dicts(rows)
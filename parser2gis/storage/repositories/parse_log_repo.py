from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.base import BaseRepository


class ParseLogRepo(BaseRepository):
    table = "parse_logs"
    columns = ["id", "task_id", "level", "message", "source", "created_at"]

    @classmethod
    def create(cls, task_id: int, level: str, message: str,
               source: str | None = None) -> dict[str, Any]:
        conn = cls._conn()
        cursor = conn.execute(
            "INSERT INTO parse_logs (task_id, level, message, source) VALUES (?, ?, ?, ?)",
            (task_id, level, message, source),
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def find_by_task_id(cls, task_id: int) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM parse_logs WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def find_by_task_and_level(cls, task_id: int, level: str) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM parse_logs WHERE task_id = ? AND level = ? ORDER BY id",
            (task_id, level),
        ).fetchall()
        return cls._rows_to_dicts(rows)
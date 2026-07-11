from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.base import BaseRepository


class ExportRepo(BaseRepository):
    table = "exports"
    columns = ["id", "task_id", "format", "file_path", "record_count", "status", "error_message", "created_at"]

    @classmethod
    def create(cls, task_id: int, fmt: str, file_path: str,
               record_count: int = 0, status: str = "running") -> dict[str, Any]:
        conn = cls._conn()
        cursor = conn.execute(
            "INSERT INTO exports (task_id, format, file_path, record_count, status) VALUES (?, ?, ?, ?, ?)",
            (task_id, fmt, file_path, record_count, status),
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def complete(cls, export_id: int, record_count: int, status: str = "done",
                 error_message: str | None = None) -> dict[str, Any] | None:
        conn = cls._conn()
        conn.execute(
            "UPDATE exports SET status = ?, record_count = ?, error_message = ? WHERE id = ?",
            (status, record_count, error_message, export_id),
        )
        return cls.get_by_id(export_id)

    @classmethod
    def find_by_task_id(cls, task_id: int) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM exports WHERE task_id = ? ORDER BY created_at DESC",
            (task_id,),
        ).fetchall()
        return cls._rows_to_dicts(rows)
from __future__ import annotations

from typing import Any

from parser2gis.storage.repositories.base import BaseRepository


VALID_STATUSES = {"created", "running", "paused", "done", "error"}


class TaskRepo(BaseRepository):
    table = "tasks"
    columns = [
        "id", "name", "city_id", "rubric_id", "status", "progress",
        "orgs_found", "orgs_saved", "errors_count", "checkpoint_data",
        "created_at", "updated_at", "completed_at",
    ]

    @classmethod
    def create(cls, name: str, city_id: int, rubric_id: int) -> dict[str, Any]:
        conn = cls._conn()
        cursor = conn.execute(
            "INSERT INTO tasks (name, city_id, rubric_id) VALUES (?, ?, ?)",
            (name, city_id, rubric_id),
        )
        conn.commit()
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def update_status(cls, task_id: int, status: str) -> dict[str, Any] | None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        conn = cls._conn()
        completed_at = "datetime('now')" if status in ("done", "error") else "NULL"
        conn.execute(
            f"UPDATE tasks SET status = ?, updated_at = datetime('now'), "
            f"completed_at = {completed_at} WHERE id = ?",
            (status, task_id),
        )
        conn.commit()
        return cls.get_by_id(task_id)

    @classmethod
    def update_progress(cls, task_id: int, progress: int,
                        orgs_found: int | None = None,
                        orgs_saved: int | None = None,
                        errors_count: int | None = None) -> dict[str, Any] | None:
        conn = cls._conn()
        updates = ["progress = ?", "updated_at = datetime('now')"]
        params: list[Any] = [progress]
        if orgs_found is not None:
            updates.append("orgs_found = ?")
            params.append(orgs_found)
        if orgs_saved is not None:
            updates.append("orgs_saved = ?")
            params.append(orgs_saved)
        if errors_count is not None:
            updates.append("errors_count = ?")
            params.append(errors_count)
        params.append(task_id)
        conn.execute(
            f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        conn.commit()
        return cls.get_by_id(task_id)

    @classmethod
    def update_checkpoint(cls, task_id: int, checkpoint_data: str) -> None:
        conn = cls._conn()
        conn.execute(
            "UPDATE tasks SET checkpoint_data = ?, updated_at = datetime('now') WHERE id = ?",
            (checkpoint_data, task_id),
        )
        conn.commit()

    @classmethod
    def find_by_status(cls, status: str) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY updated_at DESC",
            (status,),
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def find_by_city_rubric(cls, city_id: int, rubric_id: int) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(
            "SELECT * FROM tasks WHERE city_id = ? AND rubric_id = ? ORDER BY created_at DESC",
            (city_id, rubric_id),
        ).fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def get_summary(cls) -> dict[str, int]:
        conn = cls._conn()
        summary: dict[str, int] = {}
        for status in VALID_STATUSES:
            row = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (status,)
            ).fetchone()
            summary[status] = row[0] if row else 0
        return summary
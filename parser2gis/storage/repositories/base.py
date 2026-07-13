from __future__ import annotations

import sqlite3
from typing import Any

from parser2gis.storage.connection import ConnectionManager


class BaseRepository:
    table: str
    columns: list[str]

    @classmethod
    def _conn(cls) -> sqlite3.Connection:
        return ConnectionManager.connection()

    @classmethod
    def _row_to_dict(cls, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        return dict(row)

    @classmethod
    def _rows_to_dicts(cls, rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
        return [dict(r) for r in rows]

    @classmethod
    def get_by_id(cls, record_id: int) -> dict[str, Any] | None:
        conn = cls._conn()
        row = conn.execute(
            f"SELECT * FROM {cls.table} WHERE id = ?", (record_id,)
        ).fetchone()
        return cls._row_to_dict(row)

    @classmethod
    def get_all(cls) -> list[dict[str, Any]]:
        conn = cls._conn()
        rows = conn.execute(f"SELECT * FROM {cls.table} ORDER BY id").fetchall()
        return cls._rows_to_dicts(rows)

    @classmethod
    def delete_by_id(cls, record_id: int) -> bool:
        ConnectionManager.backup()
        conn = cls._conn()
        cursor = conn.execute(
            f"DELETE FROM {cls.table} WHERE id = ?", (record_id,)
        )
        return cursor.rowcount > 0

    @classmethod
    def count(cls) -> int:
        conn = cls._conn()
        row = conn.execute(f"SELECT COUNT(*) FROM {cls.table}").fetchone()
        return row[0] if row else 0

    @classmethod
    def exists(cls, record_id: int) -> bool:
        conn = cls._conn()
        row = conn.execute(
            f"SELECT 1 FROM {cls.table} WHERE id = ?", (record_id,)
        ).fetchone()
        return row is not None
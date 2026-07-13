from __future__ import annotations

import datetime
import sqlite3
import threading
from pathlib import Path
from typing import Any


class ConnectionManager:
    _local = threading.local()
    _db_path: str = ""
    _lock = threading.Lock()

    @classmethod
    def configure(cls, db_path: str) -> None:
        cls._db_path = db_path

    @classmethod
    def connection(cls) -> sqlite3.Connection:
        if not cls._db_path:
            cls._db_path = str(Path.home() / ".parser2gis" / "parser2gis.db")
            Path(cls._db_path).parent.mkdir(parents=True, exist_ok=True)

        conn: sqlite3.Connection | None = getattr(cls._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(cls._db_path, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.row_factory = sqlite3.Row
            cls._local.conn = conn
            cls._local.in_transaction = False
        return conn

    @classmethod
    def close(cls) -> None:
        conn: sqlite3.Connection | None = getattr(cls._local, "conn", None)
        if conn is not None:
            conn.close()
            cls._local.conn = None

    @classmethod
    def close_all(cls) -> None:
        cls.close()

    @classmethod
    def db_path(cls) -> str:
        return cls._db_path

    @classmethod
    def check_integrity(cls) -> list[str]:
        conn = cls.connection()
        row = conn.execute("PRAGMA integrity_check").fetchone()
        if row and row[0] != "ok":
            return [row[0]]
        return []

    @classmethod
    def begin(cls) -> None:
        conn = cls.connection()
        conn.execute("BEGIN IMMEDIATE")
        cls._local.in_transaction = True

    @classmethod
    def commit(cls) -> None:
        conn = cls.connection()
        conn.commit()
        cls._local.in_transaction = False
        cls.wal_checkpoint()

    @classmethod
    def rollback(cls) -> None:
        conn = cls.connection()
        conn.rollback()
        cls._local.in_transaction = False

    @classmethod
    def in_transaction(cls) -> bool:
        return getattr(cls._local, "in_transaction", False)

    @classmethod
    def backup(cls) -> str:
        src_path = cls.db_path()
        if not src_path:
            raise RuntimeError("Database path not configured")

        src = Path(src_path)
        backup_dir = src.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_path = backup_dir / f"{src.name}.{timestamp}.bak"

        # Use a dedicated connection so backup never blocks on an open tx
        src_conn = sqlite3.connect(str(src))
        dst_conn = sqlite3.connect(str(backup_path))
        try:
            src_conn.backup(dst_conn)
        finally:
            dst_conn.close()
            src_conn.close()

        return str(backup_path)

    @classmethod
    def wal_checkpoint(cls) -> None:
        conn = cls.connection()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def get_connection() -> sqlite3.Connection:
    return ConnectionManager.connection()


def configure_database(db_path: str) -> None:
    ConnectionManager.configure(db_path)
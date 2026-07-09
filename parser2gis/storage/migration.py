from __future__ import annotations

from parser2gis.storage.connection import ConnectionManager

DDL_STATEMENTS: list[str] = [
    """
    CREATE TABLE IF NOT EXISTS cities (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        source_id   TEXT,
        region      TEXT,
        created_at  TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(name)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rubrics (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        parent_id   INTEGER REFERENCES rubrics(id),
        source_id TEXT,
        sort_order  INTEGER NOT NULL DEFAULT 0,
        created_at  TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(name)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL,
        city_id         INTEGER NOT NULL REFERENCES cities(id),
        rubric_id       INTEGER NOT NULL REFERENCES rubrics(id),
        status          TEXT NOT NULL DEFAULT 'created'
                        CHECK (status IN ('created', 'running', 'paused', 'done', 'error')),
        progress        INTEGER NOT NULL DEFAULT 0
                        CHECK (progress >= 0 AND progress <= 100),
        orgs_found      INTEGER NOT NULL DEFAULT 0,
        orgs_saved      INTEGER NOT NULL DEFAULT 0,
        errors_count    INTEGER NOT NULL DEFAULT 0,
        checkpoint_data TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
        completed_at    TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS organizations (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id     INTEGER NOT NULL REFERENCES tasks(id),
        source_id   TEXT,
        name        TEXT NOT NULL,
        city        TEXT,
        address     TEXT,
        phones      TEXT,
        emails      TEXT,
        website     TEXT,
        social      TEXT,
        rubric_name TEXT,
        work_hours  TEXT,
        lat         REAL,
        lon         REAL,
        raw_json    TEXT,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS contacts (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL REFERENCES organizations(id),
        type            TEXT NOT NULL CHECK (type IN ('phone', 'email', 'website', 'social')),
        value           TEXT NOT NULL,
        is_primary       INTEGER NOT NULL DEFAULT 0,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS exports (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id         INTEGER NOT NULL REFERENCES tasks(id),
        format          TEXT NOT NULL CHECK (format IN ('xlsx', 'csv', 'json')),
        file_path       TEXT NOT NULL,
        record_count    INTEGER NOT NULL DEFAULT 0,
        status          TEXT NOT NULL DEFAULT 'done'
                        CHECK (status IN ('running', 'done', 'error')),
        error_message   TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS parse_logs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id         INTEGER NOT NULL REFERENCES tasks(id),
        level           TEXT NOT NULL DEFAULT 'info'
                        CHECK (level IN ('debug', 'info', 'warning', 'error')),
        message         TEXT NOT NULL,
        source          TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
]

INDEX_STATEMENTS: list[str] = [
    "CREATE INDEX IF NOT EXISTS idx_organizations_task_id ON organizations(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_organizations_source_id ON organizations(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_city_id ON tasks(city_id)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_rubric_id ON tasks(rubric_id)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
    "CREATE INDEX IF NOT EXISTS idx_contacts_org_id ON contacts(organization_id)",
    "CREATE INDEX IF NOT EXISTS idx_exports_task_id ON exports(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_parse_logs_task_id ON parse_logs(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_parse_logs_level ON parse_logs(level)",
]


def migrate() -> None:
    conn = ConnectionManager.connection()
    for stmt in DDL_STATEMENTS:
        conn.execute(stmt)
    for stmt in INDEX_STATEMENTS:
        conn.execute(stmt)
    conn.commit()


def get_current_version() -> int:
    conn = ConnectionManager.connection()
    cursor = conn.execute("PRAGMA user_version")
    row = cursor.fetchone()
    return row[0] if row else 0


def set_version(version: int) -> None:
    conn = ConnectionManager.connection()
    conn.execute(f"PRAGMA user_version = {version}")
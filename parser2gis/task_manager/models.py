from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class TaskStatus:
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    ERROR = "error"

    ALL = {CREATED, RUNNING, PAUSED, DONE, ERROR}

    TRANSITIONS: dict[str, set[str]] = {
        CREATED: {RUNNING, DONE, ERROR},
        RUNNING: {PAUSED, DONE, ERROR},
        PAUSED: {RUNNING, DONE, ERROR},
        DONE: set(),
        ERROR: {CREATED},
    }

    @classmethod
    def can_transition(cls, current: str, target: str) -> bool:
        return target in cls.TRANSITIONS.get(current, set())


@dataclass
class TaskInfo:
    id: int
    name: str
    city_id: int
    rubric_id: int
    city_name: str = ""
    rubric_name: str = ""
    status: str = TaskStatus.CREATED
    progress: int = 0
    orgs_found: int = 0
    orgs_saved: int = 0
    errors_count: int = 0
    checkpoint_data: str | None = None
    created_at: str = ""
    updated_at: str = ""
    completed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskInfo:
        return cls(
            id=data["id"],
            name=data["name"],
            city_id=data["city_id"],
            rubric_id=data["rubric_id"],
            city_name=data.get("city_name", ""),
            rubric_name=data.get("rubric_name", ""),
            status=data.get("status", TaskStatus.CREATED),
            progress=data.get("progress", 0),
            orgs_found=data.get("orgs_found", 0),
            orgs_saved=data.get("orgs_saved", 0),
            errors_count=data.get("errors_count", 0),
            checkpoint_data=data.get("checkpoint_data"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            completed_at=data.get("completed_at"),
        )
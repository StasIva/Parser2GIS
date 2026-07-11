from __future__ import annotations

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

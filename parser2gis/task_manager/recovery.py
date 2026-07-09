from __future__ import annotations

import json
from typing import Any

from parser2gis.storage.repositories.parse_log_repo import ParseLogRepo
from parser2gis.storage.repositories.task_repo import TaskRepo


class CrashRecovery:
    @classmethod
    def save_checkpoint(cls, task_id: int, checkpoint: dict[str, Any]) -> None:
        TaskRepo.update_checkpoint(task_id, json.dumps(checkpoint, ensure_ascii=False))

    @classmethod
    def load_checkpoint(cls, task_id: int) -> dict[str, Any] | None:
        task = TaskRepo.get_by_id(task_id)
        if not task or not task.get("checkpoint_data"):
            return None
        try:
            return json.loads(task["checkpoint_data"])
        except (json.JSONDecodeError, TypeError):
            return None

    @classmethod
    def resume_task(cls, task_id: int) -> dict[str, Any] | None:
        task = TaskRepo.get_by_id(task_id)
        if not task:
            return None
        if task["status"] not in ("running", "paused"):
            return None
        return cls.load_checkpoint(task_id)

    @classmethod
    def recover_interrupted(cls) -> list[dict[str, Any]]:
        running_tasks = TaskRepo.find_by_status("running")
        for task in running_tasks:
            TaskRepo.update_status(task["id"], "error")
            ParseLogRepo.create(task["id"], "error",
                                "Task was interrupted by application crash",
                                source="recovery")
        return TaskRepo.find_by_status("error")
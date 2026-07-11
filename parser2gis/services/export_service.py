from __future__ import annotations

from parser2gis.domain.models import ExportRecord
from parser2gis.storage.repositories.export_repo import ExportRepo


class ExportService:
    def create(self, task_id: int, fmt: str, file_path: str,
               record_count: int = 0, status: str = "running") -> ExportRecord:
        data = ExportRepo.create(task_id, fmt, file_path, record_count, status)
        return ExportRecord.from_dict(data)

    def complete(self, export_id: int, record_count: int, status: str = "done",
                 error_message: str | None = None) -> ExportRecord:
        data = ExportRepo.complete(export_id, record_count, status, error_message)
        return ExportRecord.from_dict(data)

    def find_by_task_id(self, task_id: int) -> list[ExportRecord]:
        return [ExportRecord.from_dict(d) for d in ExportRepo.find_by_task_id(task_id)]

from __future__ import annotations

import csv
from typing import Any, Callable

from parser2gis.exporter.base import BaseExporter

CSV_COLUMNS: list[str] = [
    "id", "name", "city", "address", "phones", "emails",
    "website", "rubric_name", "work_hours", "lat", "lon", "source_id",
]


class CsvExporter(BaseExporter):
    def __init__(self, encoding: str = "utf-8-sig") -> None:
        self._encoding = encoding

    def export(self, records: list[dict[str, Any]], file_path: str,
               on_progress: Callable[[int, int], None] | None = None) -> str:
        with open(file_path, "w", newline="", encoding=self._encoding) as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            for idx, record in enumerate(records):
                writer.writerow([
                    record.get("id", ""),
                    record.get("name", ""),
                    record.get("city", ""),
                    record.get("address", ""),
                    record.get("phones", ""),
                    record.get("emails", ""),
                    record.get("website", ""),
                    record.get("rubric_name", ""),
                    record.get("work_hours", ""),
                    record.get("lat", ""),
                    record.get("lon", ""),
                    record.get("source_id", ""),
                ])
                if on_progress:
                    on_progress(idx + 1, len(records))
        return file_path
from __future__ import annotations

import json
from typing import Any, Callable

from parser2gis.exporter.base import BaseExporter


class JsonExporter(BaseExporter):
    def export(self, records: list[dict[str, Any]], file_path: str,
               on_progress: Callable[[int, int], None] | None = None) -> str:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)
        if on_progress:
            on_progress(len(records), len(records))
        return file_path
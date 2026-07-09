from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class BaseExporter(ABC):
    @abstractmethod
    def export(self, records: list[dict[str, Any]], file_path: str,
               on_progress: Callable[[int, int], None] | None = None) -> str:
        ...
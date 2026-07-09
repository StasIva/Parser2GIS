from __future__ import annotations

import json
import time
from typing import Any


class MemoryCache:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self._data: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Any | None:
        entry = self._data.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._data[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = time.monotonic() + (ttl if ttl is not None else self._ttl)
        self._data[key] = (expires_at, value)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()

    def to_json(self) -> str:
        serializable: dict[str, tuple[float, Any]] = {}
        for k, (exp, v) in self._data.items():
            serializable[k] = (exp, v)
        return json.dumps(serializable, ensure_ascii=False, default=str)

    @classmethod
    def from_json(cls, data: str, ttl_seconds: int = 300) -> MemoryCache:
        cache = cls(ttl_seconds)
        raw: dict[str, list[Any]] = json.loads(data)
        for k, (exp, v) in raw.items():
            cache._data[k] = (exp, v)
        return cache
from __future__ import annotations

from typing import Any

from parser2gis.source_2gis.http_client import HttpClient

RUBRIC_SEARCH_URL = "https://catalog.api.2gis.com/2.0/catalog/rubric/search"


class RubricResolver:
    def __init__(self, client: HttpClient, api_key: str = "") -> None:
        self._client = client
        self._api_key = api_key

    def resolve(self, rubric_name: str) -> dict[str, Any] | None:
        params: dict[str, str] = {"q": rubric_name, "limit": "10"}
        if self._api_key:
            params["key"] = self._api_key
        response = self._client.get(RUBRIC_SEARCH_URL, params=params)
        data = response.json()
        items: list[dict[str, Any]] = data.get("result", {}).get("items", []) or data.get("items", []) or []
        if not items:
            return None
        for item in items:
            name = (item.get("name") or "").lower()
            if rubric_name.lower() in name:
                return {
                    "id": str(item.get("id", "")),
                    "name": item.get("name", ""),
                    "parent_name": (item.get("parent") or {}).get("name"),
                    "parent_id": str((item.get("parent") or {}).get("id", "")) if item.get("parent") else None,
                }
        return None

    def search(self, query: str) -> list[dict[str, Any]]:
        params: dict[str, str] = {"q": query}
        if self._api_key:
            params["key"] = self._api_key
        response = self._client.get(RUBRIC_SEARCH_URL, params=params)
        data = response.json()
        items: list[dict[str, Any]] = data.get("result", {}).get("items", []) or data.get("items", []) or []
        return [
            {
                "id": str(item.get("id", "")),
                "name": item.get("name", ""),
                "parent_name": (item.get("parent") or {}).get("name"),
            }
            for item in items
        ]
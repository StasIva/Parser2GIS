from __future__ import annotations

from typing import Any

from parser2gis.source_2gis.http_client import HttpClient

CITY_SEARCH_URL = "https://catalog.api.2gis.com/3.0/items"


class CityResolver:
    def __init__(self, client: HttpClient, api_key: str = "") -> None:
        self._client = client
        self._api_key = api_key

    def resolve(self, city_name: str) -> dict[str, Any] | None:
        params: dict[str, str] = {"q": city_name, "limit": "5", "type": "adm_div.city"}
        if self._api_key:
            params["key"] = self._api_key
        response = self._client.get(CITY_SEARCH_URL, params=params)
        data = response.json()
        items: list[dict[str, Any]] = (data.get("result", {}) or {}).get("items", []) or []
        if not items:
            return None
        for item in items:
            name = (item.get("name") or "").lower()
            if city_name.lower() in name:
                return {
                    "id": str(item.get("id", "")),
                    "name": item.get("name", ""),
                    "region": (item.get("region") or {}).get("name"),
                    "lat": (item.get("point") or {}).get("lat"),
                    "lon": (item.get("point") or {}).get("lon"),
                }
        return None

    def search(self, query: str) -> list[dict[str, Any]]:
        params: dict[str, str] = {"q": query, "type": "adm_div.city"}
        if self._api_key:
            params["key"] = self._api_key
        response = self._client.get(CITY_SEARCH_URL, params=params)
        data = response.json()
        items: list[dict[str, Any]] = (data.get("result", {}) or {}).get("items", []) or []
        return [
            {
                "id": str(item.get("id", "")),
                "name": item.get("name", ""),
                "region": (item.get("region") or {}).get("name"),
            }
            for item in items
        ]
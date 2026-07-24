from __future__ import annotations

from typing import Any, Callable

from parser2gis.source_2gis.http_client import HttpClient

ORG_LIST_URL = "https://catalog.api.2gis.com/3.0/items"
ORG_CARD_URL = "https://catalog.api.2gis.com/3.0/items"


class OrgFetcher:
    def __init__(self, client: HttpClient, api_key: str = "") -> None:
        self._client = client
        self._api_key = api_key

    def fetch_list(self, city_id: str, rubric_id: str, page: int = 1,
                   page_size: int = 20) -> dict[str, Any]:
        params: dict[str, str] = {
            "city_id": city_id,
            "rubric_id": rubric_id,
            "page": str(page),
            "page_size": str(page_size),
            "sort": "rating",
        }
        if self._api_key:
            params["key"] = self._api_key
        response = self._client.get(ORG_LIST_URL, params=params)
        data = response.json()
        meta = data.get("meta", {})
        if meta.get("code", 200) != 200:
            return {"items": [], "total": 0}
        return data.get("result", {})

    def fetch_card(self, org_id: str) -> dict[str, Any] | None:
        params: dict[str, str] = {"id": org_id}
        if self._api_key:
            params["key"] = self._api_key
        response = self._client.get(ORG_CARD_URL, params=params)
        data = response.json()
        meta = data.get("meta", {})
        if meta.get("code", 200) != 200:
            return None
        items = data.get("result", {}).get("items", []) or []
        return items[0] if items else None

    def fetch_all(self, city_id: str, rubric_id: str,
                  on_progress: Callable[[int, int], None] | None = None) -> list[dict[str, Any]]:
        all_orgs: list[dict[str, Any]] = []
        page = 1
        page_size = 20

        first = self.fetch_list(city_id, rubric_id, page=1, page_size=page_size)
        total = first.get("total", 0) or len(first.get("items", []) or [])
        items = first.get("items", []) or []
        all_orgs.extend(items)

        if on_progress:
            on_progress(len(all_orgs), total)

        total_pages = max(1, (total + page_size - 1) // page_size)
        for page in range(2, total_pages + 1):
            data = self.fetch_list(city_id, rubric_id, page=page, page_size=page_size)
            items = data.get("items", []) or []
            if not items:
                break
            all_orgs.extend(items)
            if on_progress:
                on_progress(len(all_orgs), total)

        return all_orgs

    def fetch_with_cards(self, city_id: str, rubric_id: str,
                         on_progress: Callable[[int, int], None] | None = None) -> list[dict[str, Any]]:
        orgs = self.fetch_all(city_id, rubric_id, on_progress=on_progress)
        result: list[dict[str, Any]] = []
        for i, org in enumerate(orgs):
            org_id = org.get("id") or ((org.get("item") or {}).get("id") or "")
            if org_id:
                card = self.fetch_card(org_id)
                if card:
                    result.append(card)
                    continue
            result.append(org)
            if on_progress:
                on_progress(i + 1, len(orgs))
        return result
from __future__ import annotations

from typing import Any

from parser2gis.parser.address_normalizer import AddressNormalizer
from parser2gis.parser.phone_extractor import PhoneExtractor


class OrganizationParser:
    def __init__(self) -> None:
        self._address_normalizer = AddressNormalizer()
        self._phone_extractor = PhoneExtractor()

    def parse(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "source_id": self._extract_source_id(raw),
            "name": (raw.get("name") or "").strip(),
            "city": self._extract_city(raw),
            "address": self._extract_address(raw),
            "phones": self._extract_phones(raw),
            "emails": self._extract_emails(raw),
            "website": self._extract_website(raw),
            "social": self._extract_social(raw),
            "rubric_name": self._extract_rubric(raw),
            "work_hours": self._extract_hours(raw),
            "lat": self._extract_lat(raw),
            "lon": self._extract_lon(raw),
        }

    def _extract_source_id(self, raw: dict[str, Any]) -> str:
        return str(raw.get("id", raw.get("source_id", raw.get("external_id", ""))))

    def _extract_city(self, raw: dict[str, Any]) -> str:
        adv_region = raw.get("advertisement_region") or raw.get("region_name") or raw.get("city")
        if isinstance(adv_region, dict):
            return adv_region.get("name", "")
        return str(adv_region or "")

    def _extract_address(self, raw: dict[str, Any]) -> str:
        address = raw.get("address_name") or raw.get("address") or ""
        if isinstance(address, dict):
            parts = []
            for key in ("street", "building", "city"):
                val = address.get(key, "")
                if val:
                    parts.append(str(val))
            return ", ".join(parts)
        return self._address_normalizer.normalize(str(address))

    def _extract_phones(self, raw: dict[str, Any]) -> str:
        phones_raw = raw.get("phones") or raw.get("phone") or []
        if isinstance(phones_raw, str):
            phones_raw = [phones_raw]
        parsed = self._phone_extractor.extract(phones_raw)
        return "; ".join(parsed) if parsed else ""

    def _extract_emails(self, raw: dict[str, Any]) -> str:
        emails = raw.get("emails") or raw.get("email") or []
        if isinstance(emails, str):
            emails = [emails]
        return "; ".join(e.strip() for e in emails if e and e.strip())

    def _extract_website(self, raw: dict[str, Any]) -> str:
        sites = raw.get("sites") or raw.get("website") or []
        if isinstance(sites, str):
            return sites
        if isinstance(sites, list):
            items = [s for s in sites if s]
            for item in items:
                if isinstance(item, dict):
                    url = item.get("url") or item.get("href") or ""
                    if url:
                        return url
            return items[0] if items else ""
        return ""

    def _extract_social(self, raw: dict[str, Any]) -> str:
        social = raw.get("social_networks") or raw.get("social") or []
        if isinstance(social, str):
            return social
        if isinstance(social, list):
            links = []
            for item in social:
                if isinstance(item, dict):
                    url = item.get("url") or item.get("href") or ""
                    if url:
                        links.append(str(url))
                elif isinstance(item, str):
                    links.append(item)
            return "; ".join(links) if links else ""
        return ""

    def _extract_rubric(self, raw: dict[str, Any]) -> str:
        rubrics = raw.get("rubrics") or raw.get("rubric") or []
        if isinstance(rubrics, list):
            names = []
            for r in rubrics:
                if isinstance(r, dict):
                    names.append(r.get("name", ""))
                elif isinstance(r, str):
                    names.append(r)
            return "; ".join(names) if names else ""
        return ""

    def _extract_hours(self, raw: dict[str, Any]) -> str:
        hours = raw.get("working_hours") or raw.get("schedule") or raw.get("work_hours")
        if isinstance(hours, dict):
            parts = []
            for day, time_range in hours.items():
                if time_range:
                    parts.append(f"{day}: {time_range}")
            return "; ".join(parts) if parts else ""
        return str(hours or "")

    def _extract_lat(self, raw: dict[str, Any]) -> float | None:
        point = raw.get("point") or raw.get("coords") or {}
        if isinstance(point, dict):
            val = point.get("lat")
            if val is not None:
                return float(val)
        return None

    def _extract_lon(self, raw: dict[str, Any]) -> float | None:
        point = raw.get("point") or raw.get("coords") or {}
        if isinstance(point, dict):
            val = point.get("lon")
            if val is not None:
                return float(val)
        return None
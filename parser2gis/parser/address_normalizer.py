from __future__ import annotations

import re


class AddressNormalizer:
    def normalize(self, raw: str) -> str:
        if not raw:
            return ""
        address = raw.strip()
        address = re.sub(r"\s+", " ", address)
        address = address.strip(", ")
        return address

    def split(self, raw: str) -> dict[str, str]:
        parts = {
            "city": "",
            "street": "",
            "building": "",
            "postal_code": "",
        }
        if not raw:
            return parts

        address = self.normalize(raw)

        postal_match = re.match(r"^(\d{6})\s+(.*)", address)
        if postal_match:
            parts["postal_code"] = postal_match.group(1)
            address = postal_match.group(2)

        city_prefixes = r"^(г\.?\s*|город\s+|гор\.?\s*)?"
        city_match = re.match(
            rf"{city_prefixes}([А-ЯЁ][а-яё]+(?:[- ][А-ЯЁ][а-яё]+)?)\b[,.\s]*(.*)",
            address,
        )
        if city_match:
            city = city_match.group(2)
            if city not in ("ул", "улица", "пр", "проспект", "д", "дом",
                            "пер", "переулок", "б-р", "бульвар", "пл", "площадь"):
                parts["city"] = city
                address = city_match.group(3)

        street_match = re.match(
            r"(ул\.?\s*|улица\s+|пр\.?\s*|проспект\s+|пер\.?\s*|переулок\s+|"
            r"б-р\.?\s*|бульвар\s+|пл\.?\s*|площадь\s+|"
            r"ш\.?\s*|шоссе\s+)([^,]+)",
            address,
        )
        if street_match:
            parts["street"] = (street_match.group(1) + street_match.group(2)).strip()
            address = address[street_match.end():].strip(", ")
        else:
            parts["street"] = address.strip(", ")

        building_match = re.match(
            r"(?:д\.?\s*|дом\s+)?(\d+\s*[/\\]?\s*\d*[а-яА-Я]?)",
            address,
        )
        if building_match:
            parts["building"] = building_match.group(1).strip()
        elif address:
            parts["building"] = address.strip(", ")

        return parts
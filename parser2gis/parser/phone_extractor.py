from __future__ import annotations

import re


class PhoneExtractor:
    _PHONE_PATTERN = re.compile(
        r"(?:\+?7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
    )

    def extract(self, raw_phones: list[str | dict[str, str]]) -> list[str]:
        result: list[str] = []
        for entry in raw_phones:
            if isinstance(entry, dict):
                number = entry.get("number") or entry.get("phone") or entry.get("value") or ""
            else:
                number = entry
            number = re.sub(r"[\s\-\(\)]", "", number.strip())
            if not number or not re.match(r"^(\+?7|8)?\d{10}$", number):
                continue
            if not number.startswith("+") and number.startswith("8"):
                number = "+7" + number[1:]
            elif not number.startswith("+"):
                number = "+7" + number
            if number not in result:
                result.append(number)
        return result

    def is_mobile(self, phone: str) -> bool:
        cleaned = re.sub(r"\D", "", phone)
        if len(cleaned) == 11:
            cleaned = cleaned[1:]
        return cleaned.startswith("9") and len(cleaned) == 10
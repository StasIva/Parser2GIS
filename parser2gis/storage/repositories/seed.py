from __future__ import annotations

from parser2gis.storage.connection import ConnectionManager
from parser2gis.storage.migration import migrate


SEED_CITIES: list[dict[str, str | None]] = [
    {"name": "Москва", "source_id": None, "region": "Москва и Московская область"},
    {"name": "Санкт-Петербург", "source_id": None, "region": "Санкт-Петербург и Ленинградская область"},
    {"name": "Новосибирск", "source_id": None, "region": "Новосибирская область"},
]

SEED_RUBRICS: list[dict[str, object]] = [
    {"name": "Авто", "parent_id": None, "sort_order": 1},
    {"name": "Автосервис", "parent_id": None, "sort_order": 2},
    {"name": "Автозапчасти", "parent_id": None, "sort_order": 3},
    {"name": "Медицина", "parent_id": None, "sort_order": 4},
    {"name": "Клиники", "parent_id": None, "sort_order": 5},
    {"name": "Аптеки", "parent_id": None, "sort_order": 6},
    {"name": "Образование", "parent_id": None, "sort_order": 7},
    {"name": "Школы", "parent_id": None, "sort_order": 8},
    {"name": "ВУЗы", "parent_id": None, "sort_order": 9},
    {"name": "Рестораны", "parent_id": None, "sort_order": 10},
]


def seed() -> None:
    migrate()
    conn = ConnectionManager.connection()

    for city in SEED_CITIES:
        conn.execute(
            "INSERT OR IGNORE INTO cities (name, region) VALUES (?, ?)",
            (city["name"], city["region"]),
        )

    for rubric in SEED_RUBRICS:
        conn.execute(
            "INSERT OR IGNORE INTO rubrics (name, sort_order) VALUES (?, ?)",
            (rubric["name"], rubric["sort_order"]),
        )


if __name__ == "__main__":
    seed()
    print("Seed data inserted.")
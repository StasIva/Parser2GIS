# Parser2GIS

**Parser2GIS** — десктопное приложение для сбора, хранения и экспорта данных об организациях из справочников 2GIS.

## Возможности

- Поиск организаций по городу и рубрике через API 2GIS
- Нормализация и дедупликация данных (адреса, телефоны, email, сайты, часы работы, координаты)
- Локальное хранение в SQLite (WAL-режим, авто-миграция, полнотекстовый поиск)
- Экспорт в XLSX, CSV, JSON
- Десктопный интерфейс на PySide6
- CLI-интерфейс для автоматизации
- Логирование с ротацией (приложение, задачи, ошибки, экспорт)
- Обновление справочника городов и рубрик из 2GIS
- ChatGPT-экспорт (конвертация диалогов в Markdown)

## Требования

- Python 3.12+
- PySide6 (для GUI)
- httpx, openpyxl, pydantic

## Установка

```bash
git clone https://github.com/IvaStas/parser2gis.git
cd parser2gis
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -e .
```

## Использование

### Графический интерфейс

```bash
parser2gis gui
```

### Командная строка

```bash
# Запуск задачи парсинга
parser2gis run --city "Москва" --rubric "Автосервис" --output results.xlsx

# Список ресурсов
parser2gis list cities
parser2gis list rubrics
parser2gis list tasks

# Экспорт результатов
parser2gis export --task-id 1 --format xlsx --output report.xlsx

# Обновление справочника городов и рубрик
parser2gis update-directory --resource all

# Заполнение БД тестовыми данными
parser2gis seed

# Экспорт диалога ChatGPT
chatgpt-export --export-path conversations.json --conversation-id <ID> --output chat.md
```

## Сборка (portable)

```bash
pip install -e ".[build]"
python scripts/build.py
```

Готовый билд — в `dist/parser2gis/`.
Релизный архив с контрольной суммой — `dist/archive/parser2gis-<version>-<platform>-<arch>.tar.gz` + `.sha256`.

## Релиз

Полный процесс описан в [infrastructure/RELEASE.md](infrastructure/RELEASE.md).

## Структура проекта

```
parser2gis/
├── app_gui/          # Десктопный интерфейс (PySide6)
├── assets/           # Иконки и метаданные Windows
├── chatgpt_export/   # Экспорт диалогов ChatGPT
├── domain/           # Модели данных
├── exporter/         # Экспорт в XLSX/CSV/JSON
├── logging/          # Система логирования
├── parser/           # Нормализация и парсинг
├── services/         # Бизнес-логика
├── settings/         # Конфигурация
├── source_2gis/      # Интеграция с API 2GIS
├── storage/          # SQLite (репозитории, миграции)
├── task_manager/     # Управление задачами
└── __main__.py       # CLI-точка входа
```

## Данные

Приложение хранит данные в `~/.parser2gis/parser2gis.db` (SQLite, WAL-режим).
Логи — в `~/.parser2gis/logs/`.

## Лицензия

MIT © IvaStas

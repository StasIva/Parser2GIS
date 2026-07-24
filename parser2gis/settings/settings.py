from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class CityEntry(BaseModel):
    name: str
    rubric_id: str
    rubric_name: str


class UiSettings(BaseModel):
    window_width: int = 1200
    window_height: int = 800
    splitter_sizes: list[int] = [300, 900]


class AppSettings(BaseModel):
    data_directory: str = Field(
        default_factory=lambda: str(Path.home() / ".local" / "share" / "parser2gis")
    )
    max_concurrent_tasks: int = 3
    request_delay_ms: int = 500
    api_key: str = ""
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 parser2gis/0.1.0"
    )
    export_directory: str = Field(default_factory=lambda: str(Path.home() / "Desktop"))
    recent_cities: list[CityEntry] = []
    ui: UiSettings = Field(default_factory=UiSettings)
    language: str = "ru"
    theme: str = "light"


class SettingsManager:
    _config_dir: ClassVar[str] = str(Path.home() / ".config" / "parser2gis")
    _config_file: ClassVar[str] = str(Path.home() / ".config" / "parser2gis" / "settings.json")

    @classmethod
    def _ensure_config_dir(cls) -> None:
        os.makedirs(os.path.dirname(cls._config_file), exist_ok=True)

    @classmethod
    def load(cls) -> AppSettings:
        try:
            cls._ensure_config_dir()
        except OSError:
            return AppSettings()
        if not os.path.isfile(cls._config_file):
            return AppSettings()
        try:
            with open(cls._config_file, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
            return AppSettings.model_validate(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return AppSettings()

    @classmethod
    def save(cls, settings: AppSettings) -> None:
        cls._ensure_config_dir()
        with open(cls._config_file, "w", encoding="utf-8") as f:
            json.dump(settings.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    @classmethod
    def config_path(cls) -> str:
        return cls._config_file


def load_settings() -> AppSettings:
    return SettingsManager.load()

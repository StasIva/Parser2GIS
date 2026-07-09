from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

from parser2gis.settings.settings import (
    AppSettings,
    CityEntry,
    SettingsManager,
    UiSettings,
)


class TestAppSettingsDefaults:
    def test_defaults(self) -> None:
        settings = AppSettings()
        assert settings.max_concurrent_tasks == 3
        assert settings.request_delay_ms == 500
        assert settings.language == "ru"
        assert settings.theme == "light"
        assert settings.recent_cities == []

    def test_default_data_directory(self) -> None:
        settings = AppSettings()
        expected = str(Path.home() / ".local" / "share" / "parser2gis")
        assert settings.data_directory == expected

    def test_default_export_directory(self) -> None:
        settings = AppSettings()
        expected = str(Path.home() / "Desktop")
        assert settings.export_directory == expected

    def test_default_ui(self) -> None:
        settings = AppSettings()
        assert isinstance(settings.ui, UiSettings)
        assert settings.ui.window_width == 1200
        assert settings.ui.window_height == 800
        assert settings.ui.splitter_sizes == [300, 900]


class TestCityEntry:
    def test_create(self) -> None:
        city = CityEntry(name="Москва", rubric_id="1", rubric_name="Авто")
        assert city.name == "Москва"
        assert city.rubric_id == "1"
        assert city.rubric_name == "Авто"

    def test_in_app_settings(self) -> None:
        city = CityEntry(name="СПб", rubric_id="2", rubric_name="Рестораны")
        settings = AppSettings(recent_cities=[city])
        assert len(settings.recent_cities) == 1
        assert settings.recent_cities[0].name == "СПб"


class TestUiSettings:
    def test_create(self) -> None:
        ui = UiSettings(window_width=1600, window_height=900, splitter_sizes=[400, 1200])
        assert ui.window_width == 1600
        assert ui.window_height == 900
        assert ui.splitter_sizes == [400, 1200]

    def test_defaults(self) -> None:
        ui = UiSettings()
        assert ui.window_width == 1200
        assert ui.window_height == 800
        assert ui.splitter_sizes == [300, 900]


class TestSettingsManagerLoad:
    def test_load_returns_defaults_when_no_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "settings.json")
            with mock.patch.object(SettingsManager, "_config_file", new=config_file):
                settings = SettingsManager.load()
                assert isinstance(settings, AppSettings)
                assert settings.max_concurrent_tasks == 3

    def test_load_returns_defaults_on_corrupt_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "settings.json")
            with open(config_file, "w") as f:
                f.write("not json")
            with mock.patch.object(SettingsManager, "_config_file", new=config_file):
                settings = SettingsManager.load()
                assert isinstance(settings, AppSettings)
                assert settings.max_concurrent_tasks == 3

    def test_load_parses_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "settings.json")
            data = {
                "max_concurrent_tasks": 5,
                "request_delay_ms": 1000,
                "language": "en",
                "theme": "dark",
                "ui": {"window_width": 1920, "window_height": 1080, "splitter_sizes": [400, 1520]},
            }
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
            with mock.patch.object(SettingsManager, "_config_file", new=config_file):
                settings = SettingsManager.load()
                assert settings.max_concurrent_tasks == 5
                assert settings.request_delay_ms == 1000
                assert settings.language == "en"
                assert settings.theme == "dark"
                assert settings.ui.window_width == 1920
                assert settings.ui.window_height == 1080


class TestSettingsManagerSave:
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "settings.json")
            with mock.patch.object(SettingsManager, "_config_file", new=config_file):
                original = AppSettings(
                    max_concurrent_tasks=7,
                    request_delay_ms=200,
                    language="en",
                    theme="dark",
                )
                SettingsManager.save(original)
                assert os.path.isfile(config_file)
                loaded = SettingsManager.load()
                assert loaded.max_concurrent_tasks == 7
                assert loaded.request_delay_ms == 200
                assert loaded.language == "en"
                assert loaded.theme == "dark"

    def test_save_creates_config_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "nested", "dir")
            config_file = os.path.join(subdir, "settings.json")
            with mock.patch.object(SettingsManager, "_config_file", new=config_file):
                settings = AppSettings()
                SettingsManager.save(settings)
                assert os.path.isfile(config_file)


class TestLoadSettings:
    def test_load_settings_convenience(self) -> None:
        expected = AppSettings(max_concurrent_tasks=9)
        with mock.patch.object(SettingsManager, "load", return_value=expected):
            from parser2gis.settings import load_settings

            settings = load_settings()
            assert settings.max_concurrent_tasks == 9


class TestSettingsManagerConfigPath:
    def test_config_path(self) -> None:
        path = SettingsManager.config_path()
        assert path.endswith("settings.json")
        assert "parser2gis" in path

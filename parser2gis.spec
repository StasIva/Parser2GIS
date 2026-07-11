# -*- mode: python ; coding: utf-8 -*-

"""PyInstaller spec for Parser2GIS.

Produces a single-folder portable build.
Run: pyinstaller parser2gis.spec
"""

import os
from pathlib import Path

BLOCK_CIPHER_LIST = None

PROJECT_ROOT = Path(__file__).resolve().parent

DATASETS = []

# console_export.js shipped as a static data file
console_export_js = os.path.join(
    "parser2gis", "chatgpt_export", "console_export.js"
)
js_path = PROJECT_ROOT / console_export_js
if js_path.exists():
    DATASETS.append((str(js_path), "parser2gis/chatgpt_export"))

a = Analysis(
    ["parser2gis/__main__.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=DATASETS,
    hiddenimports=[
        # Lazy imports in __main__.py commands
        "parser2gis.storage.connection",
        "parser2gis.storage.migration",
        "parser2gis.storage.repositories.seed",
        "parser2gis.storage.repositories.city_repo",
        "parser2gis.storage.repositories.rubric_repo",
        "parser2gis.storage.repositories.organization_repo",
        "parser2gis.storage.repositories.task_repo",
        "parser2gis.storage.repositories.contact_repo",
        "parser2gis.storage.repositories.export_repo",
        "parser2gis.storage.repositories.parse_log_repo",
        "parser2gis.source_2gis.http_client",
        "parser2gis.source_2gis.org_fetcher",
        "parser2gis.source_2gis.city_resolver",
        "parser2gis.source_2gis.rubric_resolver",
        "parser2gis.services.organization_service",
        "parser2gis.services.city_service",
        "parser2gis.services.rubric_service",
        "parser2gis.services.task_service",
        "parser2gis.services.export_service",
        "parser2gis.logging.app_logger",
        "parser2gis.logging.error_logger",
        "parser2gis.logging.task_logger",
        "parser2gis.exporter.xlsx_exporter",
        "parser2gis.exporter.csv_exporter",
        "parser2gis.exporter.json_exporter",
        "parser2gis.app_gui.main_window",
        "parser2gis.app_gui.controllers.app_controller",
        "parser2gis.app_gui.models.task_table_model",
        "parser2gis.app_gui.widgets.progress_delegate",
        "parser2gis.app_gui.dialogs.city_rubric_dialog",
        "parser2gis.app_gui.dialogs.export_dialog",
        "parser2gis.app_gui.dialogs.settings_dialog",
        "parser2gis.app_gui.dialogs.task_name_dialog",
        "parser2gis.chatgpt_export",
        "parser2gis.chatgpt_export.cli",
        "parser2gis.chatgpt_export.markdown",
        "parser2gis.chatgpt_export.parser",
        "parser2gis.task_manager.manager",
        "parser2gis.task_manager.queue",
        "parser2gis.task_manager.recovery",
        "parser2gis.domain.models",
        "parser2gis.parser.organization_parser",
        "parser2gis.parser.address_normalizer",
        "parser2gis.parser.phone_extractor",
        "parser2gis.parser.deduplicator",
        "parser2gis.settings.settings",
        "parser2gis.storage.cache",
        # Third-party hidden imports
        "pydantic",
        "openpyxl",
        "httpx",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "PIL",
        "cv2",
        "numpy",
        "pandas",
        "notebook",
        "jupyter",
        "IPython",
        "setuptools",
        "pip",
        "packaging",
        "distutils",
        "unittest",
        "pytest",
        "curses",
        "readline",
        "test",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure, a.zipped_data, cipher_blocks=BLOCK_CIPHER_LIST)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="parser2gis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory=".",
)

COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="parser2gis",
)

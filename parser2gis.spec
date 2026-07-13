# -*- mode: python ; coding: utf-8 -*-

import os

BLOCK_CIPHER_LIST = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))

datas = []

# console_export.js shipped as a static data file
js_path = os.path.join(
    PROJECT_ROOT, "parser2gis", "chatgpt_export", "console_export.js"
)
if os.path.exists(js_path):
    datas.append((js_path, "parser2gis/chatgpt_export"))

# Application icon assets
assets_dir = os.path.join(PROJECT_ROOT, "parser2gis", "assets")
if os.path.isdir(assets_dir):
    for fname in os.listdir(assets_dir):
        fpath = os.path.join(assets_dir, fname)
        if os.path.isfile(fpath) and not fname.endswith(".rc"):
            datas.append((fpath, "parser2gis/assets"))

# Application icon
icon_path = os.path.join(PROJECT_ROOT, "parser2gis", "assets", "app_icon.ico")

a = Analysis(
    ["parser2gis/__main__.py"],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
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
        "parser2gis.logging.export_logger",
        "parser2gis.logging.log_rotation",
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
        "parser2gis.services.directory_update_service",
        "parser2gis.settings.settings",
        "parser2gis.storage.cache",
        # Third-party hidden imports
        "pydantic",
        "openpyxl",
        "httpx",
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtWidgets",
        "PySide6.QtGui",
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

pyz = PYZ(a.pure)

icon_path = os.path.join(PROJECT_ROOT, "parser2gis", "assets", "icon.ico")
version_rc_path = os.path.join(PROJECT_ROOT, "parser2gis", "assets", "version.rc")

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
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
    icon=icon_path if os.path.exists(icon_path) else None,
    version=version_rc_path if os.path.exists(version_rc_path) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="parser2gis",
)

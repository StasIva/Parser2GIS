# -*- mode: python ; coding: utf-8 -*-

import os

BLOCK_CIPHER_LIST = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ["parser2gis/__main__.py"],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "matplotlib", "scipy", "PIL", "cv2", "numpy",
        "pandas", "notebook", "jupyter", "IPython", "setuptools",
        "pip", "packaging", "distutils", "unittest", "pytest",
        "curses", "readline", "test",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

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
    console=True,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="parser2gis",
)

#!/usr/bin/env python3
"""Reproducible PyInstaller build script for Parser2GIS.

Produces a single-folder portable build at dist/parser2gis/.

Usage:
    python scripts/build.py            # full build
    python scripts/build.py --verify    # verify existing build only
    python scripts/build.py --clean     # clean build artifacts first

Requirements (installed automatically via pip):
    pyinstaller>=6.0
    All project dependencies (see pyproject.toml)

Assumptions:
    - Python 3.12+ with PySide6, httpx, openpyxl, pydantic installed.
    - Run from the project root directory.
    - Virtual environment activated (or build deps available globally).

Known limitations:
    - Playwright browser automation is NOT bundled (EPIC-9.2).
    - GUI module (PySide6) requires a display server at runtime.
    - No application icon or Windows metadata (EPIC-9.3).
    - No installer or Windows code signing (post-MVP).
    - Build tested on Linux; Windows cross-build not supported.
    - Reproducibility relies on PYTHONHASHSEED=0; exact byte-level
      reproducibility also requires matching Python/PyInstaller versions
      and the same OS platform.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "parser2gis.spec"
APP_NAME = "parser2gis"


def _print_step(msg: str) -> None:
    print(f"[build] {msg}")


def _run(*args: str, **kwargs: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=kwargs.get("check", True),
    )


def check_environment() -> None:
    _print_step("Checking environment...")

    if sys.version_info < (3, 12):
        print("Error: Python 3.12+ required", file=sys.stderr)
        sys.exit(1)

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        _print_step("PyInstaller not found, installing...")
        _run(sys.executable, "-m", "pip", "install", "pyinstaller>=6.0")
        import PyInstaller  # noqa: F401

    _print_step(f"Python {sys.version}")
    _print_step(f"PyInstaller {PyInstaller.__version__}")


def clean() -> None:
    _print_step("Cleaning build artifacts...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            _print_step(f"  Removed {d}")
    spec_stem = SPEC_FILE.stem
    for p in PROJECT_ROOT.glob(f"**/{spec_stem}.spec"):
        if p.parent == PROJECT_ROOT:
            continue
        p.unlink()
        _print_step(f"  Removed {p}")


def build() -> None:
    _print_step("Starting reproducible build...")

    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    if platform.system() == "Windows":
        env["PYINSTALLER_DETERMINISTIC"] = "1"

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--noconfirm", "--log-level=INFO"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        print("Build failed", file=sys.stderr)
        sys.exit(1)


def verify() -> None:
    _print_step("Verifying build output...")
    app_dir = DIST_DIR / APP_NAME

    if not app_dir.exists():
        print(f"Error: {app_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    # In PyInstaller 6+ the bundled content lives under _internal/
    internal_dir = app_dir / "_internal"

    if platform.system() == "Windows":
        exe_path = app_dir / f"{APP_NAME}.exe"
    else:
        exe_path = app_dir / APP_NAME

    errors: list[str] = []

    if not exe_path.exists():
        errors.append(f"Missing main executable: {exe_path}")

    # Check that application code is bundled
    app_pkg = internal_dir / "parser2gis"
    if not app_pkg.is_dir():
        errors.append(f"Missing application package: {app_pkg}")

    # Check data files
    data_file = internal_dir / "parser2gis" / "chatgpt_export" / "console_export.js"
    if not data_file.exists():
        errors.append(f"Missing data file: {data_file}")

    # Quick dry-run: executable should print help/usage
    try:
        result = subprocess.run(
            [str(exe_path), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
            env={**os.environ, "PARSER2GIS_DB_PATH": "/tmp/parser2gis_verify_test.db"},
        )
        if result.returncode != 0:
            errors.append(f"Executable --help exited with code {result.returncode}")
            if result.stderr:
                errors.append(f"  stderr: {result.stderr[:500]}")
    except FileNotFoundError:
        errors.append(f"Executable not found: {exe_path}")
    except subprocess.TimeoutExpired:
        errors.append("Executable --help timed out (15s)")

    file_count = len(list(app_dir.rglob("*")))

    if errors:
        print("Verification FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)
    else:
        _print_step(f"Verification PASSED ({file_count} files in {app_dir})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parser2GIS build script")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--verify", action="store_true", help="Verify existing build")
    args = parser.parse_args()

    if args.clean:
        clean()
        return

    if args.verify:
        verify()
        return

    check_environment()
    clean()
    build()
    verify()
    _print_step("Build complete.")


if __name__ == "__main__":
    main()

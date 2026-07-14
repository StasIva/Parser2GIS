#!/usr/bin/env python3
"""Release packaging script for Parser2GIS.

Creates a reproducible release archive (.tar.gz on Linux, .zip on Windows)
with a SHA256 checksum file.

Usage:
    python scripts/package_release.py              # package existing build
    python scripts/package_release.py --verify      # verify existing package
    python scripts/package_release.py --dist-dir PATH  # custom build output dir

Output:
    dist/parser2gis-<version>-<platform>-<arch>.tar.gz
    dist/parser2gis-<version>-<platform>-<arch>.sha256
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
APP_NAME = "parser2gis"

ARCHIVE_DIR = DIST_DIR / "archive"


def _print_step(msg: str) -> None:
    print(f"[package] {msg}")


def _get_version() -> str:
    import tomllib
    pyproject = PROJECT_ROOT / "pyproject.toml"
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def _platform_tag() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "linux":
        return f"linux-{machine}"
    if system == "windows":
        return f"windows-{machine}"
    return f"{system}-{machine}"


def _build_dir() -> Path:
    return DIST_DIR / APP_NAME


def find_build() -> Path | None:
    d = _build_dir()
    return d if d.is_dir() else None


def create_archive(archive_format: str, version: str, tag: str) -> Path:
    build_path = _build_dir()
    archive_name = f"{APP_NAME}-{version}-{tag}.{archive_format}"
    archive_path = ARCHIVE_DIR / archive_name
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    _print_step(f"Creating {archive_format} archive: {archive_name}")

    if archive_format == "tar.gz":
        with tarfile.open(archive_path, "w:gz", compresslevel=9) as tf:
            tf.add(build_path, arcname=build_path.name)
    elif archive_format == "zip":
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in build_path.rglob("*"):
                zf.write(file, arcname=f"{build_path.name}/{file.relative_to(build_path)}")
    else:
        raise ValueError(f"Unsupported archive format: {archive_format}")

    _print_step(f"Archive created: {archive_path} ({archive_path.stat().st_size:,} bytes)")
    return archive_path


def create_checksum(archive_path: Path) -> Path:
    sha256 = hashlib.sha256()
    with open(archive_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)

    checksum_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    checksum_content = f"{sha256.hexdigest()}  {archive_path.name}\n"
    checksum_path.write_text(checksum_content)

    _print_step(f"Checksum: {checksum_path} ({sha256.hexdigest()})")
    return checksum_path


def verify_archive(archive_path: Path) -> bool:
    checksum_path = archive_path.with_suffix(archive_path.suffix + ".sha256")

    if not checksum_path.exists():
        print(f"Error: checksum file not found: {checksum_path}", file=sys.stderr)
        return False

    sha256 = hashlib.sha256()
    with open(archive_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)

    stored = checksum_path.read_text().strip().split()[0]
    computed = sha256.hexdigest()

    if stored == computed:
        _print_step(f"Verification PASSED for {archive_path.name}")
        return True
    else:
        print(f"Verification FAILED for {archive_path.name}", file=sys.stderr)
        print(f"  Stored:   {stored}", file=sys.stderr)
        print(f"  Computed: {computed}", file=sys.stderr)
        return False


def clean() -> None:
    if ARCHIVE_DIR.exists():
        shutil.rmtree(ARCHIVE_DIR)
        _print_step(f"Removed {ARCHIVE_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Package Parser2GIS release archive")
    parser.add_argument("--verify", action="store_true", help="Verify existing archives")
    parser.add_argument("--clean", action="store_true", help="Clean archive directory")
    parser.add_argument("--format", choices=["tar.gz", "zip"], default=None,
                        help="Archive format (default: tar.gz on Linux, zip on Windows)")
    args = parser.parse_args()

    if args.clean:
        clean()
        return

    build_path = find_build()
    if build_path is None:
        print(f"Error: no build found at {_build_dir()}", file=sys.stderr)
        print("Run 'python scripts/build.py' first.", file=sys.stderr)
        sys.exit(1)

    version = _get_version()
    tag = _platform_tag()

    if args.verify:
        archives = [p for p in ARCHIVE_DIR.glob(f"{APP_NAME}-{version}-{tag}.*")
                    if not p.suffix == ".sha256"]
        if not archives:
            print(f"No archives found for {APP_NAME}-{version}-{tag}", file=sys.stderr)
            sys.exit(1)
        all_ok = all(verify_archive(a) for a in archives)
        sys.exit(0 if all_ok else 1)

    if args.format:
        archive_format = args.format
    else:
        archive_format = "zip" if platform.system() == "Windows" else "tar.gz"

    archive_path = create_archive(archive_format, version, tag)
    create_checksum(archive_path)

    _print_step(f"Package complete: {ARCHIVE_DIR / archive_path.name}")


if __name__ == "__main__":
    main()

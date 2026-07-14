# Release Process

## Overview

This document describes the release process for Parser2GIS.
Each release produces a portable build archive with a checksum file.

## Prerequisites

- Python 3.12+
- Git
- GitHub account with push access to `github.com/IvaStas/parser2gis`
- GitHub Actions enabled on the repository

## Release Steps

### 1. Prepare the release

```bash
# Ensure you are on main with all changes merged
git checkout main
git pull

# Verify the version in pyproject.toml
grep 'version = ' pyproject.toml
```

### 2. Build

```bash
pip install -e ".[build]"
python scripts/build.py
```

### 3. Package

```bash
python scripts/package_release.py
```

Output:
- `dist/archive/parser2gis-<version>-<platform>-<arch>.tar.gz`
- `dist/archive/parser2gis-<version>-<platform>-<arch>.tar.gz.sha256`

### 4. Run tests

```bash
python -m pytest tests/
```

### 5. Push and tag

```bash
git tag v<version>
git push origin main --tags
```

The Windows CI build (`build-windows.yml`) runs automatically via GitHub Actions on tag push.

### 6. Create GitHub release

1. Go to https://github.com/IvaStas/parser2gis/releases
2. Click "Draft a new release"
3. Choose the tag `v<version>`
4. Upload the archives from `dist/archive/`
5. Publish the release

### 7. Windows Defender submission

The Windows CI workflow (`.github/workflows/build-windows.yml`) runs automatically on:
- Push to `main`
- Tag push (`v*`)
- Pull request to `main`
- Manual trigger via GitHub Actions UI (`workflow_dispatch`)

After the Windows CI build completes and produces a Windows artifact:

1. Go to **GitHub → Actions → Build Windows → workflow run**
2. Download the `parser2gis-windows` artifact
3. On a Windows machine (or in CI), package the artifact:
   ```bash
   python scripts/package_release.py --format zip
   ```
4. Submit to Microsoft Defender portal:
   - https://www.microsoft.com/en-us/wdsi/filesubmission
   - Upload the Windows archive from `dist/archive/parser2gis-<version>-windows-x86_64.zip`
   - For **Product name**: `Parser2GIS`
   - For **File description**: `Parser2GIS — desktop application for collecting and exporting organization data from 2GIS city directories`
   - For **Vendor**: `IvaStas`
   - Select **"False positive"** as the reason
   - In the notes: `This is a Python application packaged with PyInstaller. It uses PySide6 for GUI, httpx for HTTP requests, and openpyxl for Excel export. The false positive is likely caused by PyInstaller's bootloader and bundled Python environment.`
   - Wait for review (typically 1-3 business days)

After Defender approves, the executable will be whitelisted and won't trigger Defender alerts on user machines.

### 8. Verify release

- [ ] Build artifact created for all target platforms
- [ ] Checksum file matches archive
- [ ] Tests pass on CI
- [ ] Windows Defender submission completed
- [ ] Release published on GitHub
- [ ] Release tagged in git

## Archive naming convention

```
parser2gis-<version>-<platform>-<arch>.<ext>
parser2gis-<version>-<platform>-<arch>.<ext>.sha256
```

Examples:
- `parser2gis-0.1.0-linux-x86_64.tar.gz`
- `parser2gis-0.1.0-windows-x86_64.zip`

## Versioning

Parser2GIS follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: incompatible changes
- **MINOR**: new functionality (backward compatible)
- **PATCH**: bug fixes (backward compatible)

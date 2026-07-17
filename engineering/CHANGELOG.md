# Engineering Standards Changelog

---

## v1.0 — Initial Engineering Standards

Introduced a formal engineering process for the Parser2GIS project.

### Added

- Engineering Constitution
- AI Engineering Playbook
- Code Review Checklist
- Task Template
- AI_README entry point

### Purpose

Create a repeatable engineering workflow for AI agents working on the project.

### Validation

The standards were validated through an Engineering Standards Adoption Review performed by Paperclip Orchestrator.

Results:

- Engineering documentation successfully adopted.
- Constitution compliance review completed.
- Documentation inconsistencies identified and corrected.
- Engineering process confirmed operational.

---

## v1.1 — Reproducible PyInstaller Build Pipeline

Added a reproducible PyInstaller build pipeline for Parser2GIS.

### Added

- `parser2gis.spec` — PyInstaller spec for single-folder portable build
- `scripts/build.py` — Entry-point build script with verification
- `pyproject.toml` build dependencies in `[project.optional-dependencies] build`

### Changed

- `parser2gis/workspace.py` — Skip git workspace validation when running in a PyInstaller bundle (`sys.frozen`)

### Notes

- Build is reproducible via `PYTHONHASHSEED=0` and deterministic flags.
- PySide6 GUI dependencies are bundled (requires display server at runtime).
- See `scripts/build.py --help` for usage.

---

## v1.2 — App Icon, Windows Metadata & Directory Update

### Added

- Application icon: `app_icon.ico`, `icon.ico`, PNGs for all sizes, SVG source
- `scripts/generate_icon.py` — SVG-to-ICO/PNG generation (rsvg-convert or Pillow fallback)
- `version.rc` — Windows VERSIONINFO with IvaStas company metadata
- `parser2gis.manifest` — Windows compatibility manifest
- `DirectoryUpdateService` — city/rubric directory update from 2GIS API
- `update-directory` CLI command and GUI dialog (Russian localization)
- `.github/workflows/build-windows.yml` — automated Windows CI build

### Changed

- `scripts/build.py` — calls `generate_icons()` and `compile_resources()` before PyInstaller
- `parser2gis.spec` — bundles assets, sets icon and version metadata
- `DirectoryUpdateService` — all public methods return strongly-typed `DirectoryUpdateResult` (R-013)

### Removed

- `directory_updater.py` — duplicate code removed (R-017)

---

---

## v1.3 — Windows CI Smoke Test with CLI Execution

### Added

- Enhanced CI smoke test to actually execute the built `parser2gis.exe` with CLI commands:
  - `--version` — verifies the binary starts and exits cleanly
  - `seed` — verifies database initialization, migrations, and seed data insertion
  - `list cities` — verifies 3 seeded cities are queryable
  - `list rubrics` — verifies 10 seeded rubrics are queryable
  - `list tasks` — verifies empty result does not crash
  - `export` — verifies graceful handling when no organizations exist

### Notes

- GUI functionality (main window, dialogs, full workflow) still requires manual testing on a real Windows environment with a display server.
- CLI-only smoke tests cover non-GUI startup, database layer, and export pipeline.

Future changes to the engineering process should be documented in this file.
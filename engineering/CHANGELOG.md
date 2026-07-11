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

Future changes to the engineering process should be documented in this file.
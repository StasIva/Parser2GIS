# 2GIS MVP — Full Backlog

## Epics

### EPIC-1: Project Foundation
**Goal:** Establish project structure, development environment, and foundational infrastructure.
**Result:** Runnable project with module structure, database, and config system.
**Dependencies:** None
**Acceptance:** `python -m parser2gis --help` prints usage.

| # | Task | Hours | Status |
|---|------|-------|--------|
| 1.1 | Scaffold Python project with pyproject.toml, venv, editorconfig, gitignore | 1 | DONE |
| 1.2 | Create directory structure (app_gui, source_2gis, storage, parser, exporter, settings, logging) | 1 | DONE |
| 1.3 | Implement SQLite connection manager with WAL mode and integrity checks | 2 | DONE |
| 1.4 | Write DDL for all tables: cities, rubrics, tasks, organizations, contacts, exports, parse_logs | 2 | DONE |
| 1.5 | Implement auto-migration script (create tables if not exist, add indexes) | 1 | DONE |
| 1.6 | Implement Settings manager (JSON config file, defaults) | 2 | DONE |
| 1.7 | Implement base repository class with common CRUD operations | 2 | DONE |
| 1.8 | Implement CityRepo (CRUD, find by name, find by source_id) | 1 | DONE |
| 1.9 | Implement RubricRepo (CRUD, tree queries, find by name) | 2 | DONE |
| 1.10 | Seed test data: 3 cities + 10 rubrics for development | 1 | DONE |

### EPIC-2: 2GIS Data Source
**Goal:** Reliably collect organization data from 2GIS public interface.
**Result:** Python module that, given city + rubric, returns normalized organization records.
**Dependencies:** EPIC-1
**Acceptance:** 50+ real organizations collected from 2GIS for Москва/Автосервис.
**Status:** DONE

| # | Task | Hours | Status |
|---|------|-------|--------|
| 2.1 | Research 2GIS public data endpoints (web, API, map tiles) | 3 | DONE |
| 2.2 | Implement HTTP client with configurable headers and timeouts | 3 | DONE |
| 2.3 | Implement city search/resolve (translate city name → 2GIS city ID) | 2 | DONE |
| 2.4 | Implement rubric search/resolve (translate rubric → 2GIS rubric ID) | 2 | DONE |
| 2.5 | Implement organization list fetch by city + rubric | 4 | DONE |
| 2.6 | Implement individual organization card fetch | 4 | DONE |
| 2.7 | Implement rate limiter with configurable delay and burst | 2 | DONE |
| 2.8 | Implement retry with exponential backoff (max 3 retries) | 2 | DONE |
| 2.9 | Implement user-agent rotation | 1 | DONE |
| 2.10 | Implement browser-based fallback with Playwright | 6 | TODO |

### EPIC-3: Parser & Normalization
**Goal:** Convert raw 2GIS data into clean, structured organization records.
**Result:** Normalized Organization objects with deduplication.
**Dependencies:** EPIC-2
**Acceptance:** Parsed records have all core fields filled; duplicates are rejected.
**Status:** DONE

| # | Task | Hours | Status |
|---|------|-------|--------|
| 3.1 | Implement OrganizationParser — extract core fields from 2GIS response | 3 | DONE |
| 3.2 | Implement address normalizer (city, street, building, postal code) | 2 | DONE |
| 3.3 | Implement phone extractor + formatter (multiple phones, mobile detection) | 3 | DONE |
| 3.4 | Implement email extractor | 1 | DONE |
| 3.5 | Implement website/social extractor | 1 | DONE |
| 3.6 | Implement work hours parser | 1 | DONE |
| 3.7 | Implement coordinates extractor (lat/lon) | 1 | DONE |
| 3.8 | Implement deduplication engine (source_id, URL, name+address) | 2 | DONE |
| 3.9 | Implement raw JSON storage for debugging | 1 | TODO |
| 3.10 | Implement batch processing (chunked save for large result sets) | 2 | TODO |

### EPIC-4: Task Management
**Goal:** Create, manage, and track parsing tasks.
**Result:** Full task lifecycle with status tracking and progress reporting.
**Dependencies:** EPIC-1
**Acceptance:** Task status transitions match spec (created → running → done/error).
**Status:** DONE

| # | Task | Hours | Status |
|---|------|-------|--------|
| 4.1 | Implement Task data class and enums (created, running, paused, done, error) | 1 | DONE |
| 4.2 | Implement TaskRepo (CRUD, status updates, progress tracking) | 2 | DONE |
| 4.3 | Implement TaskManager — create task, validate city+rubric, manage lifecycle | 3 | DONE |
| 4.4 | Implement async task queue (QThreadPool or asyncio) | 4 | DONE |
| 4.5 | Implement pause/resume/stop for running tasks | 3 | DONE |
| 4.6 | Implement crash recovery (save checkpoint, resume from last org) | 3 | DONE |
| 4.7 | Implement progress tracking (orgs found, saved, errors) | 2 | DONE |
| 4.8 | Implement TaskContextMenu actions (view, export single, reset, rerun, delete, open folder) | 2 | TODO |
| 4.9 | Implement task count/summary endpoint | 1 | DONE |

### EPIC-5: Storage & Data Layer
**Goal:** Robust, performant local data storage.
**Result:** All data persisted with indexes, integrity checks, and export support.
**Dependencies:** EPIC-1
**Acceptance:** 10,000 records stored and queried in <1 second.
**Status:** PARTIAL (5.7, 5.8 remain)

| # | Task | Hours | Status |
|---|------|-------|--------|
| 5.1 | Implement OrganizationRepo (save, find, deduplicate, search) | 2 | DONE |
| 5.2 | Implement ContactRepo (save contacts per organization) | 1 | DONE |
| 5.3 | Implement ExportRepo (log each export operation) | 1 | DONE |
| 5.4 | Implement ParseLogRepo (per-task log entries) | 1 | DONE |
| 5.5 | Implement full-text search on organization names | 2 | DONE |
| 5.6 | Implement DB integrity check + repair on startup | 2 | DONE |
| 5.7 | Implement DB backup before destructive operations | 1 | TODO |
| 5.8 | Implement automatic WAL checkpoint | 1 | TODO |

### EPIC-6: GUI Application
**Goal:** Desktop interface matching 2GIS Parser reference video.
**Result:** Full-featured desktop application with all dialogs.
**Dependencies:** EPIC-4
**Acceptance:** User can complete full workflow without touching CLI.
**Status:** DONE

| # | Task | Hours | Status |
|---|------|-------|--------|
| 6.1 | Implement MainWindow with toolbar, task table, status bar | 4 | DONE |
| 6.2 | Implement TaskTableModel with Qt MVC pattern | 3 | DONE |
| 6.3 | Implement toolbar buttons (Create, Start, Stop, Settings) | 2 | DONE |
| 6.4 | Implement CityRubricDialog with tree view and search | 5 | DONE |
| 6.5 | Implement TaskNameDialog with auto-generation | 2 | DONE |
| 6.6 | Implement progress column (0–100% with status text) | 2 | DONE |
| 6.7 | Implement ExportDialog (format, path, progress, success) | 3 | DONE |
| 6.8 | Implement SettingsDialog (threads, delays, paths, proxy) | 3 | DONE |
| 6.9 | Implement AppController — wire all GUI to TaskManager | 4 | DONE |
| 6.10 | Implement status bar with task count and last action | 2 | DONE |
| 6.11 | Implement Russian localization for all UI strings | 3 | DONE |
| 6.12 | Implement dark/light theme support | 2 | TODO |

### EPIC-7: Export System
**Goal:** Export organization data in multiple formats.
**Result:** XLSX, CSV, JSON exports with user-selectable options.
**Dependencies:** EPIC-5
**Acceptance:** All 3 formats produce correct output for 10,000 records.
**Status:** DONE

| # | Task | Hours | Status |
|---|------|-------|--------|
| 7.1 | Design exporter interface (abstract base class) | 1 | DONE |
| 7.2 | Implement XLSX exporter (all fields, text-formatted phones) | 4 | DONE |
| 7.3 | Implement CSV exporter with UTF-8 BOM and Windows-1251 options | 3 | DONE |
| 7.4 | Implement JSON exporter | 2 | DONE |
| 7.5 | Implement multi-task export (all / selected) | 2 | TODO |
| 7.6 | Implement export progress callback | 2 | DONE |
| 7.7 | Implement export validation (verify file, count rows) | 2 | TODO |
| 7.8 | Implement export notification (success dialog with count) | 1 | DONE |

### EPIC-8: Logging & Diagnostics
**Goal:** Comprehensive logging for debugging and monitoring.
**Result:** Separate logs for app, tasks, source errors, and exports.
**Dependencies:** EPIC-1
**Acceptance:** All errors are logged; source errors are clearly separated.
**Status:** DONE

| # | Task | Hours | Status |
|---|------|-------|--------|
| 8.1 | Implement application-wide logger (file + console) | 2 | DONE |
| 8.2 | Implement per-task logger (separate file per task) | 2 | DONE |
| 8.3 | Implement source error logger (2GIS errors only) | 1 | DONE |
| 8.4 | Implement export logger | 1 | DONE |
| 8.5 | Implement task summary reporter (completion stats) | 2 | DONE |
| 8.6 | Implement log rotation and max size limits | 1 | DONE |
| 8.7 | Implement user-friendly error messages (Russian) | 2 | DONE |

### EPIC-9: Build & Distribution
**Goal:** Portable Windows application ready for distribution.
**Result:** Single-folder portable build; user manual; release archive.
**Dependencies:** EPIC-6, EPIC-7, EPIC-8
**Acceptance:** Build runs on clean Windows 10/11 without Python.

| # | Task | Hours | Status |
|---|------|-------|--------|
| 9.1 | Write PyInstaller spec file + build script | 3 | DONE |
| 9.2 | Configure PyInstaller hooks for PySide6, Playwright/Selenium | 3 | DONE |
| 9.3 | Add application icon and Windows metadata | 1 | DONE |
| 9.4 | Implement city/rubric directory update mechanism | 3 | DONE |
| 9.5 | Write user manual (Russian) | 4 | TODO |
| 9.6 | Write README in Russian | 1 | TODO |
| 9.7 | Create release archive with checksum | 1 | TODO |
| 9.8 | Smoke test on Linux VM | 2 | DONE |
| 9.8a | Windows smoke test via CI (GitHub Actions) | 2 | TODO |
| 9.9 | Submit to Windows Defender for false positive mitigation | 2 | TODO |

### EPIC-10: CLI & API (Post-MVP)
**Goal:** Headless operation and programmatic access.
**Result:** CLI commands and local REST API.
**Dependencies:** EPIC-3, EPIC-4
**Acceptance:** All major operations available via CLI flags.

| # | Task | Hours | Status |
|---|------|-------|--------|
| 10.1 | Implement CLI entry point with argparse/subcommands | 2 | TODO |
| 10.2 | `parser2gis run` — run task from CLI | 2 | TODO |
| 10.3 | `parser2gis export` — export results | 1 | TODO |
| 10.4 | `parser2gis list` — list tasks/cities/rubrics | 1 | TODO |
| 10.5 | `parser2gis update-rubrics` — update directory | 1 | TODO |
| 10.6 | Implement local REST API (FastAPI or Flask) | 4 | TODO |
| 10.7 | API: GET /cities, GET /rubrics | 1 | TODO |
| 10.8 | API: POST /tasks, GET /tasks/{id}, POST /tasks/{id}/start | 2 | TODO |
| 10.9 | API: GET /tasks/{id}/organizations, GET /tasks/{id}/export | 2 | TODO |

## Phase Assignment Backlog

### Immediate (MVP Sprint — Stage 1) ✅ COMPLETE
EPIC-1 (Foundation) — Tasks 1.1–1.10
EPIC-2 (2GIS Source) — Tasks 2.1–2.9 (except 2.10)
EPIC-3 (Parser) — Tasks 3.1–3.8 (core fields only)
EPIC-8 (Logging) — Tasks 8.1, 8.3, 8.7

### Stage 2 ✅ COMPLETE
EPIC-6 (GUI) — Tasks 6.1–6.11
EPIC-4 (Task Mgmt) — Tasks 4.1–4.3 (basic)

### Stage 3 ✅ COMPLETE
EPIC-4 (Task Mgmt) — Tasks 4.4–4.9
EPIC-5 (Storage) — Tasks 5.1–5.6
EPIC-8 (Logging) — Tasks 8.2, 8.5

### Stage 4 ✅ COMPLETE
EPIC-7 (Export) — Tasks 7.1–7.8
EPIC-2 (2GIS Source) — Task 2.10 (browser fallback)

### Stage 5 — REMAINING
EPIC-9 (Build) — Tasks 9.1–9.9a (Linux smoke test done; Windows CI tracked as 9.8a)
EPIC-5 (Storage) — Tasks 5.7, 5.8
EPIC-8 (Logging) — Tasks 8.4, 8.6

### Post-MVP
EPIC-10 (CLI/API) — Tasks 10.1–10.9
EPIC-3 (Parser) — Tasks 3.9, 3.10
EPIC-7 (Export) — Tasks 7.5, 7.7

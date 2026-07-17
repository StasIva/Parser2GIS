# Windows Smoke Test Report — Parser2GIS v0.1.0

**Date:** 2026-07-17
**Epic:** EPIC-9.8a — Windows Smoke Test via CI
**Tester:** Automated CI (GitHub Actions, `windows-latest`)
**Environment:** Headless (no display server)

## Scope

Validate that the Parser2GIS MVP can be installed and used on a clean Windows environment, as verified through automated CI. This report covers **CLI functionality only** (GUI requires manual testing on a real desktop).

## Test Results

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Application builds successfully | ✅ PASS | PyInstaller produces `dist/parser2gis/parser2gis.exe` |
| 2 | Executable is ≥ 1 MB | ✅ PASS | Sanity check against degenerate build |
| 3 | `--version` prints version string | ✅ PASS | Binary starts and exits cleanly |
| 4 | `seed` command runs (DB init + migration + seed data) | ✅ PASS | SQLite database initializes, migrations run, 3 cities + 10 rubrics inserted |
| 5 | `list cities` returns seeded cities | ✅ PASS | Москва, Санкт-Петербург, Новосибирск present |
| 6 | `list rubrics` returns seeded rubrics | ✅ PASS | All 10 seed rubrics present |
| 7 | `list tasks` does not crash on empty set | ✅ PASS | Returns empty output, exit code 0 |
| 8 | `export` handles missing data gracefully | ✅ PASS | Exits with code 1 and descriptive error (no orgs for task 0) |
| 9 | Unit tests pass (non-fatal) | ✅ PASS | Non-fatal per CI workflow design |
| 10 | Artifact uploads successfully | ✅ PASS | `parser2gis-windows` artifact available for download |

## Cannot Test in CI (Manual Testing Required)

| # | Check | Reason |
|---|-------|--------|
| 11 | Main window opens | Requires display server / desktop session |
| 12 | No startup exceptions in GUI | Same — GUI imports PySide6 which needs a display |
| 13 | Open an input file | GUI operation |
| 14 | Execute parsing | Requires 2GIS API access + GUI context |
| 15 | Export results via GUI | GUI operation |
| 16 | Verify exported file via GUI | GUI operation |
| 17 | Application exits normally from GUI | GUI operation |

## Discovered Issues

**None.** The Windows CI workflow builds, tests, and executes CLI commands successfully. No regressions or new bugs were found during smoke testing.

## Recommendations

1. **Manual GUI smoke test** — Run `dist/parser2gis/parser2gis.exe` on a real Windows 10/11 machine and verify the GUI checklist (items 11–17 above).
2. **Windows Defender exclusion** — Antivirus may flag PyInstaller-built executables. Plan for EPIC-9.9 (false positive mitigation).

## Deliverables Status

- [x] Smoke Test Report (this document)
- [x] Enhanced CI workflow with CLI execution smoke tests
- [x] Backlog updated (EPIC-9.8a → DONE)
- [x] CHANGELOG updated (v1.3)

## Build Artifact

Available from the latest successful CI run: `parser2gis-windows` artifact on GitHub Actions.

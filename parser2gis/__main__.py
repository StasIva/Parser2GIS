from __future__ import annotations

import argparse
import sys

from parser2gis.workspace import validate_workspace


def main() -> None:
    validate_workspace()

    parser = argparse.ArgumentParser(
        prog="parser2gis",
        description="Collect, store, and export organization data from 2GIS city directories",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="parser2gis 0.1.0",
    )
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="Run a parsing task")
    run_parser.add_argument("--city", required=True, help="City name")
    run_parser.add_argument("--rubric", required=True, help="Rubric name")
    run_parser.add_argument("--output", help="Output file path for export")

    list_parser = sub.add_parser("list", help="List resources")
    list_parser.add_argument("resource", choices=["cities", "rubrics", "tasks"],
                             help="Resource type to list")

    export_parser = sub.add_parser("export", help="Export task results")
    export_parser.add_argument("--task-id", type=int, required=True, help="Task ID")
    export_parser.add_argument("--format", choices=["xlsx", "csv", "json"],
                               default="xlsx", help="Export format")
    export_parser.add_argument("--output", required=True, help="Output file path")

    seed_parser = sub.add_parser("seed", help="Seed database with test data")

    gui_parser = sub.add_parser("gui", help="Launch the desktop application")

    args = parser.parse_args()

    if args.command == "run":
        _cmd_run(args)
    elif args.command == "list":
        _cmd_list(args)
    elif args.command == "export":
        _cmd_export(args)
    elif args.command == "seed":
        _cmd_seed()
    elif args.command == "gui":
        _cmd_gui()
    else:
        parser.print_help()
        sys.exit(0)


def _cmd_run(args: argparse.Namespace) -> None:
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.migration import migrate
    from parser2gis.storage.repositories.seed import seed
    from parser2gis.source_2gis.http_client import HttpClient
    from parser2gis.source_2gis.org_fetcher import OrgFetcher
    from parser2gis.storage.repositories.organization_repo import OrganizationRepo
    from parser2gis.logging.app_logger import AppLogger

    configure_database("")
    migrate()
    seed()

    client = HttpClient(delay_ms=500)
    fetcher = OrgFetcher(client)

    city = _resolve_city(args.city)
    if not city:
        print(f"City '{args.city}' not found", file=sys.stderr)
        sys.exit(1)

    rubric = _resolve_rubric(args.rubric)
    if not rubric:
        print(f"Rubric '{args.rubric}' not found", file=sys.stderr)
        sys.exit(1)

    AppLogger.info(f"Fetching organizations for {city['name']}/{rubric['name']}")

    def _on_progress(found: int, total: int) -> None:
        print(f"  Progress: {found}/{total}", end="\r")

    orgs = fetcher.fetch_all(str(city.get("id") or city.get("source_id", "")),
                             str(rubric.get("id") or rubric.get("source_id", "")),
                             on_progress=_on_progress)

    print(f"\nFound {len(orgs)} organizations")

    saved = 0
    for org in orgs:
        OrganizationRepo.create(task_id=0, name=org.get("name", ""),
                                source_id=str(org.get("id", "")),
                                city=org.get("city", ""),
                                address=org.get("address", ""))
        saved += 1

    print(f"Saved {saved} organizations")

    client.close()


def _cmd_list(args: argparse.Namespace) -> None:
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.migration import migrate
    from parser2gis.storage.repositories.seed import seed

    configure_database("")
    migrate()
    seed()

    if args.resource == "cities":
        from parser2gis.storage.repositories.city_repo import CityRepo
        for city in CityRepo.get_all():
            print(f"  {city['id']}: {city['name']}")
    elif args.resource == "rubrics":
        from parser2gis.storage.repositories.rubric_repo import RubricRepo
        for rubric in RubricRepo.get_all():
            print(f"  {rubric['id']}: {rubric['name']}")
    elif args.resource == "tasks":
        from parser2gis.storage.repositories.task_repo import TaskRepo
        for task in TaskRepo.get_all():
            print(f"  {task['id']}: {task['name']} [{task['status']}]")


def _cmd_export(args: argparse.Namespace) -> None:
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.migration import migrate
    from parser2gis.storage.repositories.organization_repo import OrganizationRepo
    from parser2gis.exporter.xlsx_exporter import XlsxExporter
    from parser2gis.exporter.csv_exporter import CsvExporter
    from parser2gis.exporter.json_exporter import JsonExporter

    configure_database("")
    migrate()

    orgs = OrganizationRepo.find_by_task_id(args.task_id)
    if not orgs:
        print(f"No organizations found for task {args.task_id}")
        sys.exit(1)

    exporters = {
        "xlsx": XlsxExporter(),
        "csv": CsvExporter(),
        "json": JsonExporter(),
    }
    exporter = exporters[args.format]
    path = exporter.export(orgs, args.output)
    print(f"Exported {len(orgs)} records to {path}")


def _cmd_seed() -> None:
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.repositories.seed import seed

    configure_database("")
    seed()
    print("Database seeded with cities and rubrics.")


def _cmd_gui() -> None:
    from PySide6.QtWidgets import QApplication
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.migration import migrate
    from parser2gis.storage.repositories.seed import seed
    from parser2gis.app_gui.main_window import MainWindow

    configure_database("")
    migrate()
    seed()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def _resolve_city(name: str) -> dict | None:
    from parser2gis.storage.repositories.city_repo import CityRepo
    return CityRepo.find_by_name(name)


def _resolve_rubric(name: str) -> dict | None:
    from parser2gis.storage.repositories.rubric_repo import RubricRepo
    return RubricRepo.find_by_name(name)


if __name__ == "__main__":
    main()
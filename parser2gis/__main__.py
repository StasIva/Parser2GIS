from __future__ import annotations

import argparse
import sys

from parser2gis.workspace import validate_workspace


def main() -> None:
    validate_workspace()
    sys.stdout.reconfigure(encoding='utf-8')

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

    update_parser = sub.add_parser("update-directory", help="Update city and rubric directory from 2GIS API")
    update_parser.add_argument("--resource", choices=["cities", "rubrics", "all"],
                                default="all", help="Which resource to update")

    chatgpt_parser = sub.add_parser("chatgpt-export", help="Export a ChatGPT conversation to markdown")
    chatgpt_parser.add_argument("--export-path", required=True,
                                 help="Path to ChatGPT conversations.json (from data export)")
    chatgpt_parser.add_argument("--conversation-id", required=True,
                                 help="Conversation ID or URL (e.g. 6a4f46fe-b788-83eb-a1ea-7233173bc656)")
    chatgpt_parser.add_argument("--output", required=True, help="Output .md file path")
    chatgpt_parser.add_argument("--handoff", action="store_true",
                                 help="Generate a handoff document instead of plain markdown")

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
    elif args.command == "update-directory":
        _cmd_update_directory(args)
    else:
        parser.print_help()
        sys.exit(0)


def _cmd_run(args: argparse.Namespace) -> None:
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.migration import migrate
    from parser2gis.storage.repositories.seed import seed
    from parser2gis.source_2gis.http_client import HttpClient
    from parser2gis.source_2gis.org_fetcher import OrgFetcher
    from parser2gis.services.organization_service import OrganizationService
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

    AppLogger.info(f"Fetching organizations for {city.name}/{rubric.name}")

    def _on_progress(found: int, total: int) -> None:
        print(f"  Progress: {found}/{total}", end="\r")

    orgs = fetcher.fetch_all(str(city.id or city.source_id or ""),
                             str(rubric.id or rubric.source_id or ""),
                             on_progress=_on_progress)

    print(f"\nFound {len(orgs)} organizations")

    org_service = OrganizationService()
    saved = 0
    for org in orgs:
        org_service.create(task_id=0, name=org.get("name", ""),
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
    from parser2gis.services.city_service import CityService
    from parser2gis.services.rubric_service import RubricService
    from parser2gis.services.task_service import TaskService

    configure_database("")
    migrate()
    seed()

    if args.resource == "cities":
        for city in CityService().get_all():
            print(f"  {city.id}: {city.name}")
    elif args.resource == "rubrics":
        for rubric in RubricService().get_all():
            print(f"  {rubric.id}: {rubric.name}")
    elif args.resource == "tasks":
        for task in TaskService().get_all():
            print(f"  {task.id}: {task.name} [{task.status}]")


def _cmd_export(args: argparse.Namespace) -> None:
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.migration import migrate
    from parser2gis.services.organization_service import OrganizationService
    from parser2gis.exporter.xlsx_exporter import XlsxExporter
    from parser2gis.exporter.csv_exporter import CsvExporter
    from parser2gis.exporter.json_exporter import JsonExporter

    configure_database("")
    migrate()

    orgs = OrganizationService().find_by_task_id(args.task_id)
    if not orgs:
        print(f"No organizations found for task {args.task_id}")
        sys.exit(1)

    exporters = {
        "xlsx": XlsxExporter(),
        "csv": CsvExporter(),
        "json": JsonExporter(),
    }
    exporter = exporters[args.format]
    path = exporter.export([o.to_dict() for o in orgs], args.output)
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


def _cmd_chatgpt_export(args: argparse.Namespace) -> None:
    from parser2gis.chatgpt_export import (
        parse_conversations_json,
        find_conversation_by_id,
        conversation_to_markdown,
        conversation_to_handoff,
    )

    conv_id = args.conversation_id
    if conv_id.startswith("https://chatgpt.com/c/"):
        conv_id = conv_id.replace("https://chatgpt.com/c/", "").split("?")[0]

    conversations = parse_conversations_json(args.export_path)
    conv = find_conversation_by_id(conversations, conv_id)
    if not conv:
        print(f"Conversation {conv_id} not found in {args.export_path}", file=sys.stderr)
        print(f"Available conversations: {len(conversations)} total", file=sys.stderr)
        sys.exit(1)

    if args.handoff:
        md = conversation_to_handoff(conv)
    else:
        md = conversation_to_markdown(conv)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Exported {len(conv.messages)} messages to {args.output}")


def _cmd_update_directory(args: argparse.Namespace) -> None:
    from parser2gis.storage.connection import configure_database
    from parser2gis.storage.migration import migrate
    from parser2gis.storage.repositories.seed import seed
    from parser2gis.services.directory_update_service import DirectoryUpdateService
    from parser2gis.source_2gis.http_client import HttpClient

    configure_database("")
    migrate()
    seed()

    client = HttpClient(delay_ms=200)
    updater = DirectoryUpdateService(client)

    resource = args.resource or "all"
    result = updater.update_all() if resource == "all" else (
        updater.update_cities() if resource == "cities" else updater.update_rubrics()
    )

    updater.close()

    if resource in ("all", "cities"):
        print(
            f"Cities: {result.cities_found} found, "
            f"{result.cities_added} added, "
            f"{result.cities_updated} updated"
        )
    if resource in ("all", "rubrics"):
        print(
            f"Rubrics: {result.rubrics_found} found, "
            f"{result.rubrics_added} added, "
            f"{result.rubrics_updated} updated"
        )
    if result.errors:
        print("Errors:", file=sys.stderr)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)


def _resolve_rubric(name: str) -> Rubric | None:
    from parser2gis.services.rubric_service import RubricService
    from parser2gis.domain.models import Rubric
    return RubricService().find_by_name(name)


if __name__ == "__main__":
    main()

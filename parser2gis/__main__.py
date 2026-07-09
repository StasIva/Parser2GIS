"""Entry point: CLI or GUI launch."""

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
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()

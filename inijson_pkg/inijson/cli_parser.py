import argparse
from .config import VERSION, DESCRIPTION, TO_JSON_HELP, TO_INI_HELP


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="inijson", description=DESCRIPTION)
    parser.add_argument("--version", action="version", version=VERSION)

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    to_json_parser = subparsers.add_parser("to-json", help=TO_JSON_HELP)
    to_json_parser.add_argument("--input", required=True, help="Input INI file path")

    to_ini_parser = subparsers.add_parser("to-ini", help=TO_INI_HELP)
    to_ini_parser.add_argument("--input", required=True, help="Input JSON file path")

    validate_parser = subparsers.add_parser("validate", help="Validate an INI file for syntax errors")
    validate_parser.add_argument("--input", required=True, help="Input INI file path to validate")

    merge_parser = subparsers.add_parser("merge", help="Merge two INI config files")
    merge_parser.add_argument("--base", required=True, help="Base INI file path")
    merge_parser.add_argument("--override", required=True, help="Override INI file path")
    merge_parser.add_argument(
        "--strategy",
        choices=["overwrite", "keep-first", "append"],
        default="overwrite",
        help="Merge strategy for conflicting keys (default: overwrite)",
    )
    merge_parser.add_argument(
        "--output-format",
        choices=["ini", "json"],
        default="ini",
        help="Output format for merged result (default: ini)",
    )

    return parser

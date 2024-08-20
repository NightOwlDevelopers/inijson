import sys
import json
from .errors import IniJsonError
from .reader import read_file
from .converter import ini_to_json, json_to_ini
from .cli_parser import get_parser


def main():
    parser = get_parser()
    if len(sys.argv) == 1:
        parser.print_usage(sys.stderr)
        sys.exit(2)

    parsed_args = parser.parse_args()

    if not parsed_args.command:
        parser.print_usage(sys.stderr)
        sys.exit(2)

    try:
        if parsed_args.command == "to-json":
            content = read_file(parsed_args.input)
            result = ini_to_json(content)
            print(result)
            sys.exit(0)

        if parsed_args.command == "to-ini":
            content = read_file(parsed_args.input)
            result = json_to_ini(content)
            print(result)
            sys.exit(0)

        if parsed_args.command == "validate":
            _run_validate(parsed_args)
            sys.exit(0)

        if parsed_args.command == "merge":
            _run_merge(parsed_args)
            sys.exit(0)

    except IniJsonError as e:
        sys.stderr.write(f"inijson: error: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"inijson: error: {e}\n")
        sys.exit(1)


def _run_validate(args) -> None:
    """Run the 'validate' subcommand: parse an INI file and report any issues."""
    from .ini_parser import ini_to_json
    content = read_file(args.input)
    # Attempt to parse; any error surfaces as IniJsonError
    result_json = ini_to_json(content)
    data = json.loads(result_json)
    section_count = len(data)
    key_count = sum(len(v) for v in data.values())
    print(f"OK: {section_count} section(s), {key_count} key(s)")


def _run_merge(args) -> None:
    """Run the 'merge' subcommand: merge two INI files."""
    from .merger import merge_configs, MergeStrategy
    strategy_map = {
        "overwrite": MergeStrategy.OVERWRITE,
        "keep-first": MergeStrategy.KEEP_FIRST,
        "append": MergeStrategy.APPEND,
    }
    strategy = strategy_map.get(getattr(args, 'strategy', 'overwrite'), MergeStrategy.OVERWRITE)

    base_content = read_file(args.base)
    override_content = read_file(args.override)

    from .merger import merge_from_strings
    merged = merge_from_strings(base_content, override_content, strategy)

    from .json_parser import json_to_ini
    merged_json = json.dumps(merged, indent=2)
    if getattr(args, 'output_format', 'ini') == 'json':
        print(merged_json)
    else:
        result = json_to_ini(merged_json)
        print(result)


if __name__ == "__main__":
    main()

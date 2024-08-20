# inijson

Bidirectional INI ↔ JSON configuration converter with a small CLI.

## Features

- Convert INI files to JSON and JSON back to INI
- Validate INI structure from the command line
- Stdlib-only Python 3.8+ (no third-party runtime dependencies)
- Preserves Python `int()` / `float()` underscore rules and float formatting semantics

## Install

```bash
pip install .
```

## CLI

```bash
inijson to-json config.ini
inijson to-ini settings.json
inijson validate config.ini
inijson --help
```

## Development

```bash
pip install -e .
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).

## Repository

Maintained by [NightOwlDevelopers](https://github.com/NightOwlDevelopers).

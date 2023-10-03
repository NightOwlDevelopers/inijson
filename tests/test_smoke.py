"""Public smoke tests for inijson (not Harbor scoring tests)."""

import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "inijson.cli", *args],
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": "src"},
    )


def test_help_lists_subcommands():
    r = _run("--help")
    assert r.returncode == 0
    assert "to-json" in r.stdout
    assert "to-ini" in r.stdout

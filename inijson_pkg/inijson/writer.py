"""INI file writer: mirrors the reader interface for round-trip support."""

import io
import os
from typing import Dict, Any, Optional, List
from .types import ini_value_to_str
from .errors import ConverterExecutionError


class IniWriter:
    """
    Writes an INI-format document from a dict-of-dicts data structure.

    Usage::

        writer = IniWriter(indent=0, comment_char=';')
        writer.write_section('database', {'host': 'localhost', 'port': 5432})
        result = writer.to_string()
    """

    def __init__(
        self,
        indent: int = 0,
        comment_char: str = ';',
        key_separator: str = ' = ',
    ) -> None:
        self._indent = indent
        self._comment_char = comment_char
        self._key_sep = key_separator
        self._buf = io.StringIO()
        self._first_section = True

    def write_comment(self, text: str) -> None:
        """Append a comment line to the output."""
        self._buf.write(f"{self._comment_char} {text}\n")

    def write_section(self, name: str, keys: Dict[str, Any]) -> None:
        """Write a complete [section] block with all its key=value pairs."""
        if not isinstance(keys, dict):
            raise ConverterExecutionError(
                f"Section '{name}' value must be a dict, got {type(keys).__name__}"
            )
        if not self._first_section:
            self._buf.write("\n")
        self._first_section = False
        self._buf.write(f"[{name}]\n")
        for k, v in keys.items():
            self.write_key(k, v)

    def write_key(self, key: str, value: Any) -> None:
        """Write a single key=value line using INI value formatting."""
        prefix = " " * self._indent
        val_str = ini_value_to_str(value)
        self._buf.write(f"{prefix}{key}{self._key_sep}{val_str}\n")

    def to_string(self) -> str:
        """Return the accumulated INI content as a string."""
        return self._buf.getvalue().rstrip("\n")

    def write_to_file(self, path: str) -> None:
        """Write the accumulated INI content to a file."""
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(self.to_string())
        except OSError as e:
            raise ConverterExecutionError(f"Failed to write file '{path}': {e}")

    def reset(self) -> None:
        """Clear the internal buffer so the writer can be reused."""
        self._buf = io.StringIO()
        self._first_section = True


def write_to_string(
    data: Dict[str, Dict[str, Any]],
    indent: int = 0,
    comment_char: str = ';',
    key_separator: str = ' = ',
    section_comments: Optional[Dict[str, str]] = None,
) -> str:
    """
    Convenience function: convert a dict-of-dicts to an INI string.

    :param data: mapping of section_name → {key: value}
    :param indent: number of leading spaces for each key line
    :param comment_char: character used for comment lines (default ';')
    :param key_separator: separator between key and value (default ' = ')
    :param section_comments: optional mapping of section_name → comment text
    """
    if not isinstance(data, dict):
        raise ConverterExecutionError("INI data must be a dict of dicts")

    writer = IniWriter(indent=indent, comment_char=comment_char, key_separator=key_separator)
    for section_name, keys in data.items():
        if section_comments and section_name in section_comments:
            writer.write_comment(section_comments[section_name])
        writer.write_section(section_name, keys)
    return writer.to_string()


def write_to_file(
    path: str,
    data: Dict[str, Dict[str, Any]],
    **kwargs: Any,
) -> None:
    """Write dict-of-dicts to an INI file at *path*."""
    content = write_to_string(data, **kwargs)
    try:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)
    except OSError as e:
        raise ConverterExecutionError(f"Failed to write file '{path}': {e}")

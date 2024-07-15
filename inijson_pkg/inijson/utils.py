"""Shared utility helpers for the inijson package."""

from typing import Any, Dict, List, Optional


def parse_value(val_str: str) -> Any:
    """
    Convert a raw INI value string to the most specific Python type.
    Handles boolean synonyms, underscored numeric literals, and plain strings.
    """
    val_lower = val_str.strip().lower()
    if val_lower in ('true', 'yes', 'on'):
        return True
    if val_lower in ('false', 'no', 'off'):
        return False

    s = val_str.strip()
    try:
        if '.' in s or 'e' in s or 'E' in s:
            return float(s)
        else:
            return int(s)
    except ValueError:
        pass

    return val_str


def format_value(val: Any) -> str:
    """
    Format a Python value for writing into an INI file.
    Booleans are rendered as 'true'/'false'; ints and floats as their string form.
    """
    if val is None:
        return 'null'
    if isinstance(val, bool):
        return 'true' if val else 'false'
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return f'{val:g}'
    return str(val)


def strip_inline_comment(line: str, comment_chars: str = ';#') -> str:
    """
    Remove an inline comment from a key=value line.
    Only strips comments that are preceded by whitespace.
    """
    for ch in comment_chars:
        idx = line.find(f' {ch}')
        if idx != -1:
            line = line[:idx]
    return line.rstrip()


def is_section_header(line: str) -> bool:
    """Return True if *line* looks like a [section] header."""
    s = line.strip()
    return s.startswith('[') and s.endswith(']')


def extract_section_name(line: str) -> str:
    """Extract the section name from a [section] header line."""
    return line.strip()[1:-1].strip()


def split_key_value(line: str) -> Optional[tuple]:
    """
    Split a 'key = value' line into (key, value).
    Accepts both '=' and ':' as separators.
    Returns None if no separator is found.
    """
    for sep in ('=', ':'):
        if sep in line:
            parts = line.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return None


def dict_to_ordered_pairs(d: Dict[str, Any]) -> List[tuple]:
    """Return a list of (key, value) pairs preserving insertion order."""
    return list(d.items())


def flatten_ini(data: Dict[str, Dict[str, Any]], sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a dict-of-dicts INI structure into a single-level dict.
    Keys are joined with *sep*: 'section.key'.
    """
    flat: Dict[str, Any] = {}
    for section, keys in data.items():
        for key, val in keys.items():
            flat[f"{section}{sep}{key}"] = val
    return flat


def unflatten_ini(flat: Dict[str, Any], sep: str = '.') -> Dict[str, Dict[str, Any]]:
    """
    Reverse of flatten_ini: split 'section.key' keys back into a dict-of-dicts.
    Keys without a separator are placed in a '_default' section.
    """
    result: Dict[str, Dict[str, Any]] = {}
    for compound_key, val in flat.items():
        if sep in compound_key:
            section, key = compound_key.split(sep, 1)
        else:
            section, key = '_default', compound_key
        if section not in result:
            result[section] = {}
        result[section][key] = val
    return result

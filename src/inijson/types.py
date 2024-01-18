"""Value-type detection and coercion for INI file values."""

from typing import Union, Optional

# Recognised boolean synonyms — same set used in the converter.
BOOLEAN_TRUE_VALUES = frozenset({'true', 'yes', 'on', '1'})
BOOLEAN_FALSE_VALUES = frozenset({'false', 'no', 'off', '0'})

# A Python type alias for the possible coerced types.
IniValue = Union[int, float, bool, None, str]


def detect_type(s: str) -> str:
    """
    Detect the most specific type name for a raw INI string value.
    Returns one of: 'bool', 'int', 'float', 'null', 'str'.
    """
    if s is None:
        return 'null'
    stripped = s.strip()
    if stripped.lower() in ('null', 'none', '~'):
        return 'null'
    if stripped.lower() in BOOLEAN_TRUE_VALUES | BOOLEAN_FALSE_VALUES:
        return 'bool'
    # Try integer (supports underscored literals like 1_000)
    try:
        int(stripped)
        return 'int'
    except ValueError:
        pass
    # Try float (including underscored, e, E notation)
    try:
        float(stripped)
        return 'float'
    except ValueError:
        pass
    return 'str'


def coerce_ini_value(s: str) -> IniValue:
    """
    Coerce a raw INI string value to its most specific Python type.
    Handles boolean synonyms, underscored numeric literals, quoted strings.
    """
    if s is None:
        return None
    # Strip optional surrounding single or double quotes
    stripped = s.strip()
    if (stripped.startswith('"') and stripped.endswith('"')) or \
       (stripped.startswith("'") and stripped.endswith("'")):
        return stripped[1:-1]
    lower = stripped.lower()
    if lower in ('null', 'none', '~'):
        return None
    if lower in BOOLEAN_TRUE_VALUES:
        return True
    if lower in BOOLEAN_FALSE_VALUES:
        return False
    # Integer (Python 3 allows underscores)
    try:
        return int(stripped)
    except ValueError:
        pass
    # Float
    try:
        return float(stripped)
    except ValueError:
        pass
    return stripped


def ini_value_to_str(val: IniValue) -> str:
    """Convert a Python value back to an INI-appropriate string representation."""
    if val is None:
        return 'null'
    if isinstance(val, bool):
        return 'true' if val else 'false'
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        # Avoid scientific notation for common values
        return f'{val:g}'
    return str(val)


def is_truthy_string(s: str) -> bool:
    """Return True if s is a recognised truthy boolean string."""
    return s.strip().lower() in BOOLEAN_TRUE_VALUES


def is_falsy_string(s: str) -> bool:
    """Return True if s is a recognised falsy boolean string."""
    return s.strip().lower() in BOOLEAN_FALSE_VALUES


def is_boolean_string(s: str) -> bool:
    """Return True if s maps to a boolean value."""
    return s.strip().lower() in (BOOLEAN_TRUE_VALUES | BOOLEAN_FALSE_VALUES)


def is_numeric_string(s: str) -> bool:
    """Return True if s can be interpreted as an integer or float."""
    try:
        int(s.strip())
        return True
    except ValueError:
        pass
    try:
        float(s.strip())
        return True
    except ValueError:
        pass
    return False

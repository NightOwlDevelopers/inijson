"""Merge two INI configurations with configurable conflict-resolution strategies."""

from enum import Enum
from typing import Dict, Any, Optional
from .errors import MergeConflictError


class MergeStrategy(Enum):
    """
    Strategy for resolving conflicts when both configs contain the same key.

    OVERWRITE  — second config's value wins (default).
    KEEP_FIRST — first config's value is retained.
    APPEND     — values are concatenated with a delimiter (for string values).
    RAISE      — a MergeConflictError is raised on any conflict.
    """
    OVERWRITE = "overwrite"
    KEEP_FIRST = "keep_first"
    APPEND = "append"
    RAISE = "raise"


def merge_configs(
    base: Dict[str, Dict[str, Any]],
    override: Dict[str, Dict[str, Any]],
    strategy: MergeStrategy = MergeStrategy.OVERWRITE,
    append_delimiter: str = ",",
) -> Dict[str, Dict[str, Any]]:
    """
    Merge *override* into *base* and return a new dict-of-dicts.

    Sections present only in one of the inputs are included as-is.
    For sections that appear in both, individual keys are merged using *strategy*.
    """
    result: Dict[str, Dict[str, Any]] = {}

    # Preserve insertion order: base sections first, then any new override sections.
    for section in base:
        result[section] = dict(base[section])

    for section, override_keys in override.items():
        if section not in result:
            result[section] = dict(override_keys)
            continue

        for key, override_val in override_keys.items():
            if key not in result[section]:
                result[section][key] = override_val
                continue

            existing_val = result[section][key]

            if strategy == MergeStrategy.OVERWRITE:
                result[section][key] = override_val

            elif strategy == MergeStrategy.KEEP_FIRST:
                pass  # keep existing_val

            elif strategy == MergeStrategy.APPEND:
                result[section][key] = (
                    f"{existing_val}{append_delimiter}{override_val}"
                )

            elif strategy == MergeStrategy.RAISE:
                raise MergeConflictError(
                    f"Conflict in [{section}] key '{key}': "
                    f"{existing_val!r} vs {override_val!r}"
                )

    return result


def deep_merge(
    base: Dict[str, Any],
    override: Dict[str, Any],
    strategy: MergeStrategy = MergeStrategy.OVERWRITE,
) -> Dict[str, Any]:
    """
    Recursively merge two plain dicts (not necessarily INI structure).
    Nested dicts are merged recursively; leaf values use *strategy*.
    """
    result: Dict[str, Any] = {}
    all_keys = list(base) + [k for k in override if k not in base]

    for key in all_keys:
        if key in base and key in override:
            bv, ov = base[key], override[key]
            if isinstance(bv, dict) and isinstance(ov, dict):
                result[key] = deep_merge(bv, ov, strategy)
            else:
                if strategy == MergeStrategy.OVERWRITE:
                    result[key] = ov
                elif strategy == MergeStrategy.KEEP_FIRST:
                    result[key] = bv
                elif strategy == MergeStrategy.RAISE:
                    raise MergeConflictError(
                        f"Conflict for key '{key}': {bv!r} vs {ov!r}"
                    )
                else:
                    result[key] = f"{bv},{ov}"
        elif key in base:
            result[key] = base[key]
        else:
            result[key] = override[key]

    return result


def merge_from_strings(
    ini_base: str,
    ini_override: str,
    strategy: MergeStrategy = MergeStrategy.OVERWRITE,
) -> Dict[str, Dict[str, Any]]:
    """
    Parse two INI strings and merge them, returning the merged dict-of-dicts.
    This is a convenience wrapper around the parser + merge_configs.
    """
    from .ini_parser import ini_to_json
    import json

    base_json = ini_to_json(ini_base)
    override_json = ini_to_json(ini_override)
    base_dict = json.loads(base_json)
    override_dict = json.loads(override_json)
    return merge_configs(base_dict, override_dict, strategy)

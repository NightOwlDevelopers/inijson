"""Schema validation for INI files."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Pattern
from .errors import ValidationError


@dataclass
class KeyRule:
    """Rule for a single INI key within a section."""
    key: str
    required: bool = False
    expected_type: Optional[str] = None   # 'str', 'int', 'float', 'bool', or None
    default: Optional[Any] = None
    pattern: Optional[str] = None         # regex pattern the string value must match
    allowed_values: Optional[List[Any]] = None

    def _check_type(self, val: Any) -> bool:
        """Return True if val matches expected_type (if set)."""
        if self.expected_type is None:
            return True
        type_map = {
            'str': str,
            'int': int,
            'float': (int, float),
            'bool': bool,
        }
        py_type = type_map.get(self.expected_type)
        if py_type is None:
            return True
        # booleans are ints in Python — check bool before int
        if self.expected_type == 'int' and isinstance(val, bool):
            return False
        return isinstance(val, py_type)

    def _check_pattern(self, val: Any) -> bool:
        if self.pattern is None:
            return True
        return bool(re.fullmatch(self.pattern, str(val)))

    def _check_allowed(self, val: Any) -> bool:
        if self.allowed_values is None:
            return True
        return val in self.allowed_values

    def validate_value(self, val: Any) -> List[str]:
        """Return a list of violation messages for *val* (empty = OK)."""
        errors: List[str] = []
        if not self._check_type(val):
            errors.append(
                f"key '{self.key}': expected type {self.expected_type}, got {type(val).__name__}"
            )
        if not self._check_pattern(val):
            errors.append(f"key '{self.key}': value {val!r} does not match pattern {self.pattern!r}")
        if not self._check_allowed(val):
            errors.append(
                f"key '{self.key}': value {val!r} not in allowed values {self.allowed_values}"
            )
        return errors


@dataclass
class SectionSchema:
    """Schema definition for a single INI section."""
    name: str
    required: bool = False
    allow_extra_keys: bool = True
    key_rules: List[KeyRule] = field(default_factory=list)

    def _rules_by_name(self) -> Dict[str, KeyRule]:
        return {r.key: r for r in self.key_rules}

    def validate_section(self, section_data: Dict[str, Any]) -> List[str]:
        """Validate a section dict and return a list of violation messages."""
        errors: List[str] = []
        rules = self._rules_by_name()

        for rule in self.key_rules:
            if rule.required and rule.key not in section_data:
                errors.append(f"section '{self.name}': required key '{rule.key}' is missing")
            elif rule.key in section_data:
                errors.extend(rule.validate_value(section_data[rule.key]))

        if not self.allow_extra_keys:
            for key in section_data:
                if key not in rules:
                    errors.append(f"section '{self.name}': unexpected key '{key}'")
        return errors


@dataclass
class IniSchema:
    """Top-level validation schema for an entire INI document."""
    section_schemas: List[SectionSchema] = field(default_factory=list)
    allow_extra_sections: bool = True

    def _section_schemas_by_name(self) -> Dict[str, SectionSchema]:
        return {s.name: s for s in self.section_schemas}

    def validate(self, config: Dict[str, Dict[str, Any]]) -> "ValidationResult":
        """Validate *config* (a dict-of-dicts) against this schema."""
        errors: List[str] = []
        schema_map = self._section_schemas_by_name()

        for sec_schema in self.section_schemas:
            if sec_schema.required and sec_schema.name not in config:
                errors.append(f"required section '[{sec_schema.name}]' is missing")
            elif sec_schema.name in config:
                errors.extend(sec_schema.validate_section(config[sec_schema.name]))

        if not self.allow_extra_sections:
            for section in config:
                if section not in schema_map:
                    errors.append(f"unexpected section '[{section}]'")

        return ValidationResult(valid=len(errors) == 0, errors=errors)


@dataclass
class ValidationResult:
    """Result of a schema validation run."""
    valid: bool
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid

    def raise_if_invalid(self) -> None:
        """Raise ValidationError if there are any violations."""
        if not self.valid:
            msg = "; ".join(self.errors)
            raise ValidationError(f"Validation failed: {msg}")

    def summary(self) -> str:
        if self.valid:
            return "OK"
        return f"{len(self.errors)} error(s): " + "; ".join(self.errors)

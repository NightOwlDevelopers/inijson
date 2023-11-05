class IniJsonError(Exception):
    """Base exception for all inijson errors."""


class ConverterExecutionError(IniJsonError):
    """Raised when a conversion (INI→JSON or JSON→INI) fails."""


class ParseError(IniJsonError):
    """Raised when the input file cannot be parsed."""


class ValidationError(IniJsonError):
    """Raised when an INI document fails schema validation."""


class ConversionError(IniJsonError):
    """Raised when a type conversion cannot be performed."""


class MergeConflictError(IniJsonError):
    """Raised when two INI configs have irreconcilable conflicts."""


class ConfigurationError(IniJsonError):
    """Raised when CLI options are inconsistent or missing."""

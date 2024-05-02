import os
from .errors import ConverterExecutionError

def read_file(path: str) -> str:
    if not os.path.exists(path):
        raise ConverterExecutionError(f"File not found: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ConverterExecutionError(f"Failed to read file: {e}")

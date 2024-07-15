import json
from .errors import ConverterExecutionError

def json_to_ini(json_content: str) -> str:
    try:
        data = json.loads(json_content)
    except Exception as e:
        raise ConverterExecutionError(f"Malformed JSON file: {e}")
        
    if not isinstance(data, dict):
        raise ConverterExecutionError("JSON root must be an object")
        
    lines = []
    for section, keys in data.items():
        if not isinstance(keys, dict):
            raise ConverterExecutionError(f"Section {section} value must be a JSON object")
        lines.append(f"[{section}]")
        for k, v in keys.items():
            if isinstance(v, bool):
                val_str = "true" if v else "false"
            elif isinstance(v, (int, float)):
                val_str = str(v)
            elif v is None:
                val_str = "null"
            else:
                val_str = str(v)
            lines.append(f"{k} = {val_str}")
        lines.append("")
        
    return "\n".join(lines).strip()

import configparser
import json
from .errors import ConverterExecutionError
from .utils import parse_value

def ini_to_json(ini_content: str) -> str:
    config = configparser.ConfigParser(dict_type=dict)
    try:
        config.read_string(ini_content)
    except Exception as e:
        raise ConverterExecutionError(f"Malformed INI file: {e}")
        
    data = {}
    for section in config.sections():
        data[section] = {}
        for key, val in config.items(section):
            data[section][key] = parse_value(val)
            
    return json.dumps(data, indent=2)

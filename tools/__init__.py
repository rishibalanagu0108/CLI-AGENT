from tools.calculator  import calculate,  SCHEMA as _CALC_SCHEMA
from tools.search      import web_search, SCHEMA as _SEARCH_SCHEMA
from tools.file_reader import read_file,  SCHEMA as _FILE_SCHEMA

TOOL_REGISTRY: dict[str, callable] = {
    "calculate":  calculate,
    "web_search": web_search,
    "read_file":  read_file,
}

TOOL_DEFINITIONS: list[dict] = [
    _CALC_SCHEMA,
    _SEARCH_SCHEMA,
    _FILE_SCHEMA,
]

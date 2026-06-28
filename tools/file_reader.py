import os

SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a local file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum lines to return (default 100)",
                },
            },
            "required": ["path"],
        },
    },
}


def read_file(path: str, max_lines: int = 100) -> str:
    try:
        if not os.path.exists(path):
            return f"Error: file not found — {path}"
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            content = "".join(lines[:max_lines])
            return f"{content}\n… (truncated at {max_lines} lines; file has {len(lines)} total)"
        return "".join(lines)
    except Exception as e:
        return f"Error reading file: {e}"

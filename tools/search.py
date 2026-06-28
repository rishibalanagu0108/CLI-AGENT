from duckduckgo_search import DDGS

SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information on any topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (1–10, default 3)",
                },
            },
            "required": ["query"],
        },
    },
}


def web_search(query: str, num_results: int = 3) -> str:
    try:
        num_results = max(1, min(10, num_results))
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(
                f"{i}. {r.get('title', 'No title')}\n"
                f"   {r.get('href', '')}\n"
                f"   {r.get('body', '')}"
            )
        return "\n\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"

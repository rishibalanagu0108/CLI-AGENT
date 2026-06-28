# CLI Agent

A CLI agent built from scratch on the **Think → Act → Observe** loop — no LangChain, no LlamaIndex, just the Gemini API and a clean Python loop.

---

## How it works

```
User Query
    │
    ▼
┌─────────────┐
│    THINK    │  ← call Gemini with message history + tool schemas
└──────┬──────┘
       │
       ▼
 finish_reason == "tool_calls"?
       │
   YES │                    NO (stop)
       ▼                      ▼
┌─────────────┐          Return answer
│  ACT + OBS  │
│  run tools  │  ← dispatch to TOOL_REGISTRY, capture results
│  append to  │
│   history   │
└──────┬──────┘
       │
       └──────► loop back to THINK
```

The LLM never executes tools — it describes intent. You execute. Every iteration is logged.

---

## Setup

**1. Clone and create a virtual environment**

```bash
git clone <repo-url>
cd cli-agent
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Get a Gemini API key**

Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free API key.

**3. Configure credentials**

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

---

## Usage

**Single-query mode**

```bash
python main.py "What is 99 * 12?"
python main.py "Search for the latest Python release" --verbose
python main.py "Read requirements.txt and list the dependencies"
```

**Interactive REPL**

```bash
python main.py
```

```
CLI Agent  —  type 'exit' or press Ctrl-C to quit

You: What is the capital of France and 45 * 3?
Agent: The capital of France is Paris. 45 × 3 = 135.

You: exit
Goodbye!
```

**`--verbose` flag** prints token count and iteration count to stderr after each response.

---

## Tools

| Tool | Function | Description |
|------|----------|-------------|
| `calculate` | `calculate(expr)` | Safe math evaluation via AST — no `eval()` |
| `web_search` | `web_search(query, num_results)` | DuckDuckGo search, no API key required |
| `read_file` | `read_file(path, max_lines)` | Read a local file, truncates at `max_lines` |

---

## Logging

Every agent lifecycle event is logged to the console (colored) and to `agent.log` (rotating JSON lines).

| Event | Level | What it captures |
|-------|-------|-----------------|
| `agent_start` | INFO | User query |
| `agent_end` | INFO | Iterations, total tokens, wall-clock duration |
| `iteration_start` | DEBUG | Iteration number, message count |
| `llm_call_start` | INFO | Model, message count, iteration |
| `llm_call_end` | INFO | finish_reason, input/output tokens, latency |
| `tool_call` | INFO | Tool name, inputs, result (truncated), latency |
| `tool_error` | ERROR | Tool name, inputs, exception message |
| `max_iterations_hit` | WARN | Iteration limit, total tokens |

`agent.log` rotates at 5 MB and keeps 3 backups.

---

## Project structure

```
cli-agent/
├── main.py              # CLI entry point (single-query + REPL)
├── agent.py             # Think → Act → Observe loop
├── llm_interface.py     # Gemini chat completions wrapper
├── state.py             # Conversation history (OpenAI-compatible format)
├── logger.py            # Structured event logger
├── config.py            # Gemini env vars and constants
├── requirements.txt
├── .env.example
└── tools/
    ├── __init__.py      # TOOL_REGISTRY + TOOL_DEFINITIONS
    ├── calculator.py    # Safe AST-based expression evaluator
    ├── search.py        # DuckDuckGo web search
    └── file_reader.py   # Local file reader
```

---

## Configuration

All settings live in `config.py` and are read from `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `MAX_TOKENS` | `4096` | Max tokens per LLM response |
| `MAX_ITERATIONS` | `10` | Max Think→Act→Observe cycles per query |

**Available models**

| Model | Best for |
|-------|----------|
| `gemini-2.0-flash` | Fast responses, everyday tasks (default) |
| `gemini-1.5-pro` | Complex reasoning, longer context |
| `gemini-1.5-flash` | Lighter and faster alternative |

---

## Adding a new tool

1. Create `tools/your_tool.py` with a function and an OpenAI-format `SCHEMA` dict
2. Register it in `tools/__init__.py`:

```python
from tools.your_tool import your_fn, SCHEMA as _YOUR_SCHEMA

TOOL_REGISTRY["your_fn"] = your_fn
TOOL_DEFINITIONS.append(_YOUR_SCHEMA)
```

The agent picks it up automatically on the next run — no other changes needed.

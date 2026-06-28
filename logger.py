import json
import logging
import time
from logging.handlers import RotatingFileHandler

# ANSI color codes
_RESET  = "\033[0m"
_GREY   = "\033[38;5;245m"
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RED    = "\033[31m"
_BOLD   = "\033[1m"

_LEVEL_COLORS = {
    "DEBUG":    _GREY,
    "INFO":     _CYAN,
    "WARNING":  _YELLOW,
    "ERROR":    _RED,
    "CRITICAL": _RED + _BOLD,
}


class _ColorConsoleFormatter(logging.Formatter):
    def format(self, record):
        color = _LEVEL_COLORS.get(record.levelname, _RESET)
        ts    = self.formatTime(record, "%H:%M:%S")
        level = f"{color}{record.levelname:<7}{_RESET}"
        name  = f"{_GREY}{record.name}{_RESET}"
        return f"{_GREY}{ts}{_RESET} {level} {name} — {record.getMessage()}"


class _JsonFileFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts":      self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level":   record.levelname,
            "event":   getattr(record, "event", record.getMessage()),
        }
        payload.update(getattr(record, "extra", {}))
        return json.dumps(payload)


class AgentLogger:
    def __init__(self, name: str = "agent", log_file: str = "agent.log"):
        self._log = logging.getLogger(name)
        self._log.setLevel(logging.DEBUG)

        if not self._log.handlers:
            # Console — colored
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(_ColorConsoleFormatter())
            self._log.addHandler(ch)

            # File — JSON lines, rotating at 5 MB
            fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(_JsonFileFormatter())
            self._log.addHandler(fh)

    def _emit(self, level: int, event: str, **fields):
        record = self._log.makeRecord(
            self._log.name, level, "(logger)", 0,
            event, (), None,
        )
        record.event = event
        record.extra = fields
        self._log.handle(record)

    # ── Public event methods ───────────────────────────────────────────────

    def log_agent_start(self, query: str):
        self._emit(logging.INFO, "agent_start",
                   query=query[:120] + ("…" if len(query) > 120 else ""))

    def log_agent_end(self, iterations: int, total_tokens: int, duration_ms: float):
        self._emit(logging.INFO, "agent_end",
                   iterations=iterations, total_tokens=total_tokens,
                   duration_ms=round(duration_ms, 1))

    def log_iteration_start(self, iteration: int, message_count: int):
        self._emit(logging.DEBUG, "iteration_start",
                   iteration=iteration, message_count=message_count)

    def log_llm_call_start(self, deployment: str, message_count: int, iteration: int):
        self._emit(logging.INFO, "llm_call_start",
                   deployment=deployment, message_count=message_count, iteration=iteration)

    def log_llm_call_end(self, finish_reason: str, input_tokens: int,
                         output_tokens: int, duration_ms: float):
        self._emit(logging.INFO, "llm_call_end",
                   finish_reason=finish_reason, input_tokens=input_tokens,
                   output_tokens=output_tokens, duration_ms=round(duration_ms, 1))

    def log_tool_call(self, name: str, inputs: dict, result: str, duration_ms: float):
        self._emit(logging.INFO, "tool_call",
                   tool=name, inputs=inputs,
                   result=result[:200] + ("…" if len(result) > 200 else ""),
                   duration_ms=round(duration_ms, 1))

    def log_tool_error(self, name: str, inputs: dict, error: str):
        self._emit(logging.ERROR, "tool_error",
                   tool=name, inputs=inputs, error=error)

    def log_max_iterations_hit(self, limit: int, total_tokens: int):
        self._emit(logging.WARNING, "max_iterations_hit",
                   limit=limit, total_tokens=total_tokens)

    def log_rate_limit(self, attempt: int, max_retries: int, retry_after_s: float):
        self._emit(logging.WARNING, "rate_limit_retry",
                   attempt=attempt, max_retries=max_retries,
                   retry_after_s=round(retry_after_s, 1),
                   message=f"Rate limited — waiting {retry_after_s:.0f}s then retrying ({attempt}/{max_retries})")


# Module-level singleton — callers do: from logger import logger
logger = AgentLogger()


if __name__ == "__main__":
    # Quick self-test
    t0 = time.perf_counter()
    logger.log_agent_start("What is the capital of France and 45 * 3?")
    logger.log_iteration_start(1, 2)
    logger.log_llm_call_start("gpt-4o", 2, 1)
    logger.log_llm_call_end("tool_calls", 120, 45, 312.4)
    logger.log_tool_call("calculate", {"expr": "45*3"}, "135", 0.3)
    logger.log_tool_call("web_search", {"query": "capital of France"}, "Paris is the capital of France.", 210.5)
    logger.log_iteration_start(2, 5)
    logger.log_llm_call_start("gpt-4o", 5, 2)
    logger.log_llm_call_end("stop", 380, 60, 290.1)
    logger.log_agent_end(2, 605, (time.perf_counter() - t0) * 1000)
    print("\nagent.log written — check JSON lines:")
    with open("agent.log") as f:
        for line in f:
            print(" ", line.rstrip())

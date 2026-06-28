import json
import time

from config import MAX_ITERATIONS
from llm_interface import LLMInterface
from logger import logger
from state import ConversationState
from tools import TOOL_DEFINITIONS, TOOL_REGISTRY


class Agent:
    def __init__(self):
        self.llm   = LLMInterface()
        self.state = ConversationState()

    def run(self, user_query: str) -> str:
        t0 = time.perf_counter()
        logger.log_agent_start(user_query)
        self.state.add_user_message(user_query)

        while self.state.iterations < MAX_ITERATIONS:
            self.state.iterations += 1
            logger.log_iteration_start(self.state.iterations, len(self.state.messages))

            # ── THINK ────────────────────────────────────────────────────
            choice, usage = self.llm.call(
                self.state.messages, TOOL_DEFINITIONS, self.state.iterations
            )
            self.state.track_tokens(usage)
            self.state.add_assistant_message(choice.message)

            # ── CHECK STOP ───────────────────────────────────────────────
            if choice.finish_reason == "stop":
                answer = choice.message.content or ""
                logger.log_agent_end(
                    self.state.iterations,
                    self.state.total_tokens,
                    (time.perf_counter() - t0) * 1000,
                )
                return answer

            # ── ACT + OBSERVE ────────────────────────────────────────────
            if choice.finish_reason == "tool_calls":
                tool_results = self._act_and_observe(choice.message.tool_calls)
                self.state.add_tool_results(tool_results)

        # Max iterations reached
        logger.log_max_iterations_hit(MAX_ITERATIONS, self.state.total_tokens)
        return f"Reached the maximum of {MAX_ITERATIONS} iterations without a final answer."

    def _act_and_observe(self, tool_calls) -> list[dict]:
        results = []
        for tc in tool_calls:
            name   = tc.function.name
            inputs = json.loads(tc.function.arguments)
            fn     = TOOL_REGISTRY.get(name)

            t0 = time.perf_counter()
            if fn is None:
                error = f"Unknown tool: {name!r}"
                logger.log_tool_error(name, inputs, error)
                result = error
            else:
                try:
                    result = fn(**inputs)
                    logger.log_tool_call(name, inputs, result, (time.perf_counter() - t0) * 1000)
                except Exception as e:
                    error = str(e)
                    logger.log_tool_error(name, inputs, error)
                    result = f"Error executing {name}: {error}"

            results.append({
                "role":         "tool",
                "tool_call_id": tc.id,
                "content":      str(result),
            })
        return results

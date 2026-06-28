import time
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    MAX_TOKENS,
)
from logger import logger


class LLMInterface:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
        )
        self.deployment = AZURE_OPENAI_DEPLOYMENT

    def call(self, messages: list[dict], tool_defs: list[dict], iteration: int):
        logger.log_llm_call_start(self.deployment, len(messages), iteration)

        t0 = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            tools=tool_defs or None,
            max_tokens=MAX_TOKENS,
        )
        duration_ms = (time.perf_counter() - t0) * 1000

        choice = response.choices[0]
        logger.log_llm_call_end(
            finish_reason=choice.finish_reason,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            duration_ms=duration_ms,
        )

        return choice, response.usage

import time
from openai import AzureOpenAI, OpenAI
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    MAX_TOKENS,
)
from logger import logger


def _make_client(endpoint: str, api_key: str, api_version: str):
    # New Azure AI Foundry endpoints already contain /v1 in the path.
    # The AzureOpenAI client appends ?api-version=... which those endpoints reject.
    # For /v1-style URLs use the standard OpenAI client with base_url instead.
    if "/v1" in endpoint:
        return OpenAI(api_key=api_key, base_url=endpoint.rstrip("/"))
    return AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
    )


class LLMInterface:
    def __init__(self):
        self.client     = _make_client(AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION)
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

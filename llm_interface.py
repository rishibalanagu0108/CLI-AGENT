import re
import time
from openai import OpenAI, AuthenticationError, NotFoundError, BadRequestError, RateLimitError
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS
from logger import logger

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_MAX_RETRIES   = 3


def _parse_retry_delay(exc: RateLimitError) -> float:
    match = re.search(r'retry[^\d]*(\d+(?:\.\d+)?)\s*s', str(exc), re.IGNORECASE)
    return float(match.group(1)) if match else 60.0


class LLMInterface:
    def __init__(self):
        self.client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url=_GROQ_BASE_URL,
        )
        self.model = GROQ_MODEL

    def call(self, messages: list[dict], tool_defs: list[dict], iteration: int):
        logger.log_llm_call_start(self.model, len(messages), iteration)

        t0 = time.perf_counter()

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tool_defs or None,
                    max_tokens=MAX_TOKENS,
                )
                break  # success — exit retry loop

            except RateLimitError as e:
                delay = _parse_retry_delay(e)
                if attempt == _MAX_RETRIES:
                    raise RuntimeError(
                        f"Groq rate limit hit {_MAX_RETRIES} times in a row.\n"
                        f"Check your usage limits at: https://console.groq.com"
                    )
                logger.log_rate_limit(attempt, _MAX_RETRIES, delay)
                time.sleep(delay)

            except AuthenticationError:
                raise RuntimeError(
                    "Groq authentication failed.\n"
                    "Check GROQ_API_KEY in your .env file.\n"
                    "Get a key at: https://console.groq.com"
                )
            except NotFoundError:
                raise RuntimeError(
                    f"Groq model '{self.model}' not found.\n"
                    "Check GROQ_MODEL in your .env file.\n"
                    "Available models: llama-3.3-70b-versatile, llama3-70b-8192, mixtral-8x7b-32768"
                )
            except BadRequestError as e:
                raise RuntimeError(f"Bad request to Groq: {e}")

        duration_ms = (time.perf_counter() - t0) * 1000

        choice = response.choices[0]
        logger.log_llm_call_end(
            finish_reason=choice.finish_reason,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            duration_ms=duration_ms,
        )

        return choice, response.usage

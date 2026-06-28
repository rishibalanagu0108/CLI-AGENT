import re
import time
from openai import OpenAI, AuthenticationError, NotFoundError, BadRequestError, RateLimitError
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_TOKENS
from logger import logger

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
_MAX_RETRIES     = 3


def _parse_retry_delay(exc: RateLimitError) -> float:
    """Pull the suggested retry delay (seconds) out of the error message, default 60s."""
    match = re.search(r'retry[^\d]*(\d+(?:\.\d+)?)\s*s', str(exc), re.IGNORECASE)
    return float(match.group(1)) if match else 60.0


class LLMInterface:
    def __init__(self):
        # Gemini exposes an OpenAI-compatible endpoint, so we reuse the
        # openai SDK — no extra dependency, same response shape.
        self.client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url=_GEMINI_BASE_URL,
        )
        self.model = GEMINI_MODEL

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
                        f"Gemini rate limit hit {_MAX_RETRIES} times in a row.\n"
                        f"Your free-tier daily quota may be exhausted.\n"
                        f"Enable billing at: https://aistudio.google.com/app/apikey"
                    )
                logger.log_rate_limit(attempt, _MAX_RETRIES, delay)
                time.sleep(delay)

            except AuthenticationError:
                raise RuntimeError(
                    "Gemini authentication failed.\n"
                    "Check GEMINI_API_KEY in your .env file.\n"
                    "Get a key at: https://aistudio.google.com/app/apikey"
                )
            except NotFoundError:
                raise RuntimeError(
                    f"Gemini model '{self.model}' not found.\n"
                    "Check GEMINI_MODEL in your .env file.\n"
                    "Available models: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash"
                )
            except BadRequestError as e:
                raise RuntimeError(f"Bad request to Gemini: {e}")

        duration_ms = (time.perf_counter() - t0) * 1000

        choice = response.choices[0]
        logger.log_llm_call_end(
            finish_reason=choice.finish_reason,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            duration_ms=duration_ms,
        )

        return choice, response.usage

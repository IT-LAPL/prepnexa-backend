"""Lightweight OpenAI client wrapper with basic validation and retry.

Keeps a single exported `call_llm(prompt)` coroutine that returns text.
"""

from openai import AsyncOpenAI
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)


# ensure key is present at import-time to fail fast
if not getattr(settings, "OPENAI_API_KEY", None):
    raise RuntimeError("OPENAI_API_KEY is not set in settings")

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def call_llm(prompt: str, *, retries: int = 2, timeout: float = 30.0) -> str:
    """Call the LLM with simple retry/backoff and return the assistant text.

    Args:
        prompt: the prompt string
        retries: number of retry attempts on transient errors
        timeout: overall request timeout in seconds (best-effort)
    """
    backoff = 1.0
    last_exc = None
    for attempt in range(retries + 1):
        try:
            # use the AsyncOpenAI client; shape may vary by SDK version
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert exam paper generator.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                ),
                timeout=timeout,
            )

            # sanitize and return text
            return response.choices[0].message.content

        except asyncio.TimeoutError as e:
            last_exc = e
            logger.warning(
                "LLM call timed out, attempt %d/%d", attempt + 1, retries + 1
            )
        except Exception as e:
            last_exc = e
            logger.exception(
                "LLM call failed on attempt %d/%d", attempt + 1, retries + 1
            )

        if attempt < retries:
            await asyncio.sleep(backoff)
            backoff *= 2

    # if we get here, all retries failed
    raise last_exc

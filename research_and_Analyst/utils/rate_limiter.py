"""
Rate-limit-aware LLM invocation helper.

Wraps LLM calls with exponential backoff retry logic to gracefully handle
Google Gemini free-tier rate limits (5 requests/minute) and other transient API errors.
"""

import time
from research_and_analyst.logger import GLOBAL_LOGGER

logger = GLOBAL_LOGGER.bind(module="RateLimiter")

# Default retry configuration
MAX_RETRIES = 5
INITIAL_WAIT_SECONDS = 15  # Start with 15s (Gemini free tier resets in ~60s)
BACKOFF_MULTIPLIER = 2     # Double the wait each retry
MAX_WAIT_SECONDS = 120     # Cap at 2 minutes

# Exception types that indicate rate limiting (checked by string match)
RATE_LIMIT_INDICATORS = [
    "ResourceExhausted",
    "429",
    "quota",
    "rate_limit",
    "RESOURCE_EXHAUSTED",
    "Too Many Requests",
]


def is_rate_limit_error(error: Exception) -> bool:
    """Check if an exception is a rate-limit / quota error."""
    error_str = str(error)
    return any(indicator.lower() in error_str.lower() for indicator in RATE_LIMIT_INDICATORS)


def invoke_with_retry(llm, messages, max_retries=MAX_RETRIES, **kwargs):
    """
    Invoke an LLM with automatic retry and exponential backoff for rate limit errors.
    
    Args:
        llm: The LangChain LLM or structured output wrapper to invoke.
        messages: The messages to pass to the LLM.
        max_retries: Maximum number of retry attempts.
        **kwargs: Additional keyword arguments passed to llm.invoke().
    
    Returns:
        The LLM response.
    
    Raises:
        The original exception if all retries are exhausted or the error is not rate-related.
    """
    wait_time = INITIAL_WAIT_SECONDS

    for attempt in range(max_retries + 1):
        try:
            return llm.invoke(messages, **kwargs)
        except Exception as e:
            if is_rate_limit_error(e) and attempt < max_retries:
                logger.warning(
                    "Rate limit hit, retrying after backoff",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    wait_seconds=wait_time,
                    error=str(e)[:200],
                )
                time.sleep(wait_time)
                wait_time = min(wait_time * BACKOFF_MULTIPLIER, MAX_WAIT_SECONDS)
            else:
                # Not a rate limit error, or we've exhausted retries — re-raise
                raise

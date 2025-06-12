"""
Robust Litellm completion() with retry and exponential backoff
"""

import time
import random
from functools import wraps
from typing import Any
from litellm import completion


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
):
    """
    Decorator for robust API calls with exponential backoff retry mechanism.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for exponential backoff
        jitter: Add random jitter to delays to avoid thundering herd
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Don't retry on final attempt
                    if attempt == max_retries:
                        break

                    # Check if error is retryable
                    if not _is_retryable_error(e):
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor**attempt), max_delay)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= 0.5 + random.random() * 0.5

                    print(
                        f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

            # If we get here, all retries failed
            raise last_exception

        return wrapper

    return decorator


def _is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is worth retrying.

    Args:
        error: The exception that occurred

    Returns:
        bool: True if the error is retryable, False otherwise
    """
    error_str = str(error).lower()
    error_type = type(error).__name__

    # Retryable HTTP status codes and error types
    retryable_conditions = [
        # Rate limiting
        "rate limit" in error_str,
        "too many requests" in error_str,
        "429" in error_str,
        # Server errors
        "500" in error_str,
        "502" in error_str,
        "503" in error_str,
        "504" in error_str,
        "internal server error" in error_str,
        "bad gateway" in error_str,
        "service unavailable" in error_str,
        "gateway timeout" in error_str,
        # Network/connection errors
        "connection" in error_str,
        "timeout" in error_str,
        "network" in error_str,
        "ssl" in error_str,
        # LiteLLM specific errors
        error_type
        in ["RateLimitError", "Timeout", "APIConnectionError", "InternalServerError"],
        # OpenAI specific errors that are retryable
        "openai" in error_str
        and any(
            x in error_str
            for x in ["rate", "timeout", "connection", "500", "502", "503"]
        ),
    ]

    return any(retryable_conditions)


@retry_on_failure(max_retries=3, base_delay=1.0, backoff_factor=2.0)
def robust_completion(**kwargs) -> Any:
    """
    Robust wrapper around litellm.completion with automatic retry mechanism.

    This function will automatically retry on transient errors like:
    - Rate limiting (429)
    - Server errors (5xx)
    - Network/connection issues
    - Timeouts

    Args:
        **kwargs: All arguments passed directly to litellm.completion()

    Returns:
        The completion response from LiteLLM

    Raises:
        Exception: Re-raises the last exception if all retries fail
    """
    return completion(**kwargs)


# Alternative: More configurable version
def create_robust_completion(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    verbose: bool = False,
):
    """
    Factory function to create a robust completion function with custom retry settings.

    Usage:
        robust_completion = create_robust_completion(max_retries=5, base_delay=2.0)
        response = robust_completion(model="gpt-4", messages=[...])
    """

    @retry_on_failure(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        jitter=jitter,
    )
    def _robust_completion(**kwargs) -> Any:
        if verbose:
            print(
                f"Making completion call with model: {kwargs.get('model', 'unknown')}"
            )
        return completion(**kwargs)

    return _robust_completion

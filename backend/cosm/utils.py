"""
Utils to make the agent more robust by make the blocks resilient to failures
"""

import time
import random
from functools import wraps
from typing import Any
from litellm import completion


import asyncio
import logging
from typing import AsyncGenerator, List

from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.agents.invocation_context import InvocationContext


# ============================================================
# Robust Litellm Completion with retry & exponential backoff
# ============================================================


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


# ==============================================
# LLMAgent with retry and exponential backoff
# ==============================================

logger = logging.getLogger(__name__)


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_retries: int = Field(default=3, ge=0, le=10)
    """Maximum number of retry attempts."""

    base_delay: float = Field(default=1.0, gt=0)
    """Base delay in seconds before first retry."""

    max_delay: float = Field(default=60.0, gt=0)
    """Maximum delay in seconds between retries."""

    backoff_multiplier: float = Field(default=2.0, gt=1.0)
    """Multiplier for exponential backoff."""

    jitter: bool = Field(default=True)
    """Add random jitter to avoid thundering herd."""

    retry_on_exceptions: List[str] = Field(
        default_factory=lambda: [
            "google.api_core.exceptions.RetryError",
            "google.api_core.exceptions.DeadlineExceeded",
            "google.api_core.exceptions.ServiceUnavailable",
            "google.api_core.exceptions.InternalServerError",
            "google.api_core.exceptions.TooManyRequests",
            "openai.RateLimitError",
            "openai.APITimeoutError",
            "openai.APIConnectionError",
            "openai.InternalServerError",
            "requests.exceptions.ConnectionError",
            "requests.exceptions.Timeout",
            "ConnectionError",
            "TimeoutError",
            "ValueError",  # For context detach errors like in your logs
        ]
    )
    """List of exception class names to retry on."""


class ResilientLlmAgent(LlmAgent):
    """
    LlmAgent wrapper with built-in retry logic and exponential backoff.

    This class extends LlmAgent to provide automatic retry functionality
    for API calls that may fail due to network issues, rate limits, or
    temporary service unavailability.
    """

    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    """Configuration for retry behavior."""

    def __init__(self, **kwargs):
        # Extract retry_config if provided
        retry_config = kwargs.pop("retry_config", None)
        super().__init__(**kwargs)

        if retry_config:
            self.retry_config = (
                retry_config
                if isinstance(retry_config, RetryConfig)
                else RetryConfig(**retry_config)
            )
        else:
            self.retry_config = RetryConfig()

    def _should_retry(self, exception: Exception) -> bool:
        """Determine if an exception should trigger a retry."""
        exception_name = (
            f"{exception.__class__.__module__}.{exception.__class__.__name__}"
        )
        simple_name = exception.__class__.__name__

        return (
            exception_name in self.retry_config.retry_on_exceptions
            or simple_name in self.retry_config.retry_on_exceptions
        )

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff with optional jitter."""
        delay = self.retry_config.base_delay * (
            self.retry_config.backoff_multiplier**attempt
        )

        # Cap at max_delay
        delay = min(delay, self.retry_config.max_delay)

        # Add jitter to avoid thundering herd
        if self.retry_config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)

    async def _retry_wrapper(self, operation_name: str, operation_func):
        """Generic retry wrapper for async operations."""
        last_exception = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return await operation_func()
            except Exception as e:
                last_exception = e

                if not self._should_retry(e):
                    logger.error(
                        f"Non-retryable error in {operation_name} for agent {self.name}: {e}"
                    )
                    raise

                if attempt >= self.retry_config.max_retries:
                    logger.error(
                        f"Max retries ({self.retry_config.max_retries}) exceeded for {operation_name} "
                        f"in agent {self.name}. Last error: {e}"
                    )
                    raise

                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{self.retry_config.max_retries + 1} failed for {operation_name} "
                    f"in agent {self.name}: {e}. Retrying in {delay:.2f}s..."
                )

                await asyncio.sleep(delay)

        # This should never be reached, but just in case
        raise last_exception

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Override with retry logic for async runs."""

        # Store reference to parent class method
        parent_run_async = super()._run_async_impl

        async def run_operation():
            events = []
            async for event in parent_run_async(ctx):
                events.append(event)
            return events

        try:
            events = await self._retry_wrapper("_run_async_impl", run_operation)
            for event in events:
                yield event
        except Exception as e:
            logger.error(
                f"Failed to run async implementation for agent {self.name}: {e}"
            )
            raise

    async def _run_live_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Override with retry logic for live runs."""

        # Store reference to parent class method
        parent_run_live = super()._run_live_impl

        async def run_operation():
            events = []
            async for event in parent_run_live(ctx):
                events.append(event)
            return events

        try:
            events = await self._retry_wrapper("_run_live_impl", run_operation)
            for event in events:
                yield event
        except Exception as e:
            logger.error(
                f"Failed to run live implementation for agent {self.name}: {e}"
            )
            raise

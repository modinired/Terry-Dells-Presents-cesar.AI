"""
Instrumentation utilities for CESAR.

This module provides decorators and metrics objects to instrument
critical functions and track their latency.  It uses the
``prometheus_client`` library to record metrics that can be scraped by a
Prometheus server.  If Prometheus is not installed, the decorators
will fall back to logging the duration to the standard logger.

Example usage::

    from utils.instrumentation import timed

    @timed
    async def process_task(self, task: dict) -> dict:
        ...

The latency of ``process_task`` will be recorded in the
``cesar_request_latency_seconds`` summary metric.
"""

from __future__ import annotations

import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Awaitable

try:
    from prometheus_client import Summary

    REQUEST_LATENCY = Summary(
        "cesar_request_latency_seconds",
        "Latency of CESAR operations"
    )

    def _observe_latency(duration: float) -> None:
        REQUEST_LATENCY.observe(duration)

except ImportError:
    logging.getLogger(__name__).warning(
        "prometheus_client is not installed; instrumentation will be logged"
    )

    def _observe_latency(duration: float) -> None:
        logging.getLogger("instrumentation").info(
            f"Operation took {duration:.6f} seconds"
        )

F = TypeVar("F", bound=Callable[..., Awaitable])

def timed(func: F) -> F:
    """Decorator to measure the execution time of an async function."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            duration = time.perf_counter() - start
            _observe_latency(duration)

    return wrapper  # type: ignore[return-value]
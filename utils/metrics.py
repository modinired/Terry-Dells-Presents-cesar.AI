"""Lightweight metrics collector for CESAR.ai runtime."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Deque, Dict, Optional


@dataclass
class MetricEvent:
    """A timestamped metric event for diagnostics timelines."""

    name: str
    value: Any
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class MetricsCollector:
    """In-memory metrics collector with async-safe helpers."""

    def __init__(self, max_events: int = 5000) -> None:
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, Any] = {}
        self._events: Deque[MetricEvent] = deque(maxlen=max_events)
        self._lock = asyncio.Lock()

    async def incr(self, name: str, value: int = 1) -> None:
        async with self._lock:
            self._counters[name] += value
            self._events.append(
                MetricEvent(name=name, value=value, timestamp=datetime.utcnow())
            )

    async def set_gauge(self, name: str, value: Any) -> None:
        async with self._lock:
            self._gauges[name] = value
            self._events.append(
                MetricEvent(name=name, value=value, timestamp=datetime.utcnow())
            )

    async def add_event(self, name: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        async with self._lock:
            self._events.append(
                MetricEvent(name=name, value=value, timestamp=datetime.utcnow(), metadata=metadata)
            )

    async def snapshot(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "recent_events": [
                    {
                        "name": event.name,
                        "value": event.value,
                        "timestamp": event.timestamp.isoformat(),
                        "metadata": event.metadata or {},
                    }
                    for event in list(self._events)[-50:]
                ],
            }


metrics = MetricsCollector()
"""Default process-wide metrics collector."""

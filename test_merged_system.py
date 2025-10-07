#!/usr/bin/env python3
"""Validate high-level SEUC orchestration helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cesar_integration_manager import CESARIntegrationManager


class _StubManager:
    def __init__(self) -> None:
        class _Agent:
            is_running = True

            async def get_performance_metrics(self):
                return {"tasks_completed": 1, "tasks_failed": 0}

            def get_capabilities(self):
                return ["analysis"]

        self.agent_fleet = {"analysis_agent": _Agent()}

        async def ci_status():
            return {
                "collective_insights": 0,
                "emergent_behaviors": 0,
                "network_size": 0,
                "network_density": 0,
                "average_trust": 0,
                "emergence_potential": 0,
            }

        async def knowledge_summary():
            return {"knowledge_topics": []}

        async def memory_status():
            return {"findings_count": 0}

        async def generate_insight(prompt: str, agents):
            return {"insight_generated": False, "prompt": prompt}

        self.collective_intelligence = SimpleNamespace(
            get_collective_intelligence_status=ci_status
        )
        self.knowledge_brain = SimpleNamespace(get_knowledge_summary=knowledge_summary)
        self.sheets_memory_manager = SimpleNamespace(get_memory_status=memory_status)
        self.generate_collective_insight = generate_insight


@pytest.mark.asyncio
async def test_initialize_seuc_processing_returns_context():
    manager = _StubManager()
    integration = CESARIntegrationManager(manager)

    context = await integration.initialize_seuc_processing(
        "Analyze financial insights", "session-1"
    )

    assert context.session_id == "session-1"
    assert any(
        capability.value == "financial_intelligence"
        for capability in context.active_capabilities
    )


@pytest.mark.asyncio
async def test_gather_multi_layer_intelligence_uses_stubs():
    manager = _StubManager()
    integration = CESARIntegrationManager(manager)

    context = await integration.initialize_seuc_processing("hello", "session-2")
    intelligence = await integration.gather_multi_layer_intelligence("hello", context)

    assert "agent_fleet" in intelligence
    assert "collective" in intelligence
    collective_layer = intelligence["collective"]
    assert collective_layer["insight_generated"] is False
    assert collective_layer["prompt"] == "hello"

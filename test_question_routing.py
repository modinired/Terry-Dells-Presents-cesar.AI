#!/usr/bin/env python3
"""Unit tests for the question router logic."""

from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from user_question_router import UserQuestionRouter


class _DummyManager:
    def __init__(self) -> None:
        self.agent_fleet = {
            "automated_reporting": object(),
            "inbox_calendar": object(),
            "spreadsheet_processor": object(),
            "crm_sync": object(),
        }


@pytest.mark.asyncio
async def test_identify_relevant_agents_matches_keywords():
    router = UserQuestionRouter(_DummyManager())

    relevant = await router._identify_relevant_agents("Need to schedule a meeting", {})

    assert "inbox_calendar" in relevant
    assert "automated_reporting" in relevant  # core agent is always present


@pytest.mark.asyncio
async def test_route_user_question_uses_broadcast_and_aggregation(monkeypatch):
    router = UserQuestionRouter(_DummyManager())

    async def fake_identify(question: str, context: dict):
        return ["automated_reporting"]

    async def fake_broadcast(question_data, agent_ids):
        return {"automated_reporting": {"success": True, "duration_ms": 12}}

    async def fake_ci(question_data, responses):
        return {"insight_generated": True}

    async def fake_aggregate(question_data, responses, ci):
        return {
            "processing_summary": {"total_agents_queried": len(responses)},
            "agent_responses": responses,
            "collective_insights": ci,
        }

    async def noop_store(question_data, response):
        return None

    monkeypatch.setattr(router, "_identify_relevant_agents", fake_identify)
    monkeypatch.setattr(router, "_broadcast_to_agents", fake_broadcast)
    monkeypatch.setattr(router, "_generate_collective_insights", fake_ci)
    monkeypatch.setattr(router, "_aggregate_responses", fake_aggregate)
    monkeypatch.setattr(router, "_store_interaction", noop_store)

    result = await router.route_user_question("How are things?", {})

    assert result["processing_summary"]["total_agents_queried"] == 1
    assert result["collective_insights"]["insight_generated"] is True

#!/usr/bin/env python3
"""Behavioral coverage for the Cursor agent in local test mode."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.cursor_agent import CursorAgent


@pytest.mark.asyncio
async def test_cursor_agent_processes_basic_task():
    agent = CursorAgent()
    try:
        await agent.initialize()
        assert agent.is_initialized is True

        status = await agent.get_status()
        assert status["cursor_connected"] is True

        task_payload = {
            "id": "test-001",
            "type": "code_review",
            "content": "def sample():\n    return True",
            "priority": "medium",
        }

        result = await agent.process_task(task_payload)
        assert result["status"] == "completed"
        assert result["task_id"] == "test-001"
    finally:
        await agent.shutdown()

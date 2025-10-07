#!/usr/bin/env python3
"""Lightweight sanity checks for the Terry Delmonaco manager."""

from __future__ import annotations

import pytest

from .main_orchestrator import TerryDelmonacoManagerAgent


@pytest.mark.asyncio
async def test_manager_metrics_structure_without_initialization():
    """`get_metrics` should work even before full orchestration is started."""

    manager = TerryDelmonacoManagerAgent()

    metrics_payload = await manager.get_metrics()

    assert metrics_payload["overall_metrics"]["total_tasks"] == 0
    assert metrics_payload["overall_metrics"]["total_completed"] == 0
    assert metrics_payload["orchestrator"]["initialized"] is False

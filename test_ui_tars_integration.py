#!/usr/bin/env python3
"""Screen recorder fallback behaviour tests."""

from __future__ import annotations

import pytest

from .core.screen_recorder import ScreenRecorder


@pytest.mark.asyncio
async def test_screen_recorder_initializes_without_ui_tars(monkeypatch):
    recorder = ScreenRecorder()

    async def fake_check_capabilities():
        return True

    async def fake_check_ui_tars():
        return False

    monkeypatch.setattr(recorder, "_check_capabilities", fake_check_capabilities)
    monkeypatch.setattr(recorder, "_check_ui_tars_integration", fake_check_ui_tars)

    assert await recorder.initialize() is True


@pytest.mark.asyncio
async def test_screen_recorder_basic_analysis_without_screenshot(monkeypatch):
    recorder = ScreenRecorder()

    analysis = await recorder.analyze_activity({"screenshot_path": None})

    assert analysis["analysis_type"] == "basic"
    assert analysis["confidence"] == 0.5

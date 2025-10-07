#!/usr/bin/env python3
"""Tests for the background agent manager analyzers."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .core.background_agent_manager import BackgroundAgentManager


@pytest.mark.asyncio
async def test_background_analyzers_detect_issues(tmp_path, monkeypatch):
    monkeypatch.setenv("CESAR_DATA_DIR", str(tmp_path))

    manager = BackgroundAgentManager()
    manager.config_file = str(Path(__file__).with_name("background_agents_config.json"))
    assert await manager.initialize() is True

    source_path = Path(__file__).with_name("test_file_with_issues.py")
    sample_content = source_path.read_text()

    bug_findings = await manager._analyze_bugs(source_path.name, sample_content)
    doc_findings = await manager._analyze_documentation(source_path.name, sample_content)
    security_findings = await manager._analyze_security(source_path.name, sample_content)

    assert any(f["issue"] == "TODO comment" for f in bug_findings)
    assert any(f["issue"] == "missing_docstring" for f in doc_findings)
    assert any(f["issue"] == "hardcoded_api_key" for f in security_findings)

    await manager.shutdown()

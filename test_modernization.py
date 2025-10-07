from pathlib import Path

import pytest

from .core.playbook_manager import PlaybookManager
from .core.workflow_engine import (
    ModernizationWorkflowEngine,
    WorkflowPhaseResult,
)
from .core.status_reporter import StatusReporter
from .utils.security_scanner import SecurityScanner
from .utils.iac_generator import IaCGenerator


def test_playbook_manager_assessment(tmp_path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("django==4.2\nmy-password-lib==1.0\n")

    manager = PlaybookManager(tmp_path)
    assessment = manager.assess_project(tmp_path)

    assert "requirements.txt" in assessment["requirements_files"][0]
    assert assessment["pin_candidates"], "Expected pinned dependency flagged"
    assert assessment["hardcoded_secret_suspects"], "Expected secret hint detected"


@pytest.mark.asyncio
async def test_workflow_engine_records_updates(tmp_path, monkeypatch):
    # Prepare lightweight project structure
    (tmp_path / "requirements.txt").write_text("fastapi==0.110\n")

    playbook_manager = PlaybookManager(tmp_path)
    status_reporter = StatusReporter()
    status_reporter.event_store_path = tmp_path / "events.json"

    security_scanner = SecurityScanner()

    async def fake_pip_audit(project_root: Path):  # pragma: no cover - deterministic stub
        return {"tool": "pip-audit", "status": "ok", "results": []}

    async def fake_secret_scan(project_root: Path):  # pragma: no cover - deterministic stub
        return {"tool": "heuristic-secret-scan", "status": "ok", "findings": []}

    monkeypatch.setattr(security_scanner, "_run_pip_audit", fake_pip_audit)
    monkeypatch.setattr(security_scanner, "_scan_for_secrets", fake_secret_scan)

    iac_generator = IaCGenerator(tmp_path / "assets")

    engine = ModernizationWorkflowEngine(
        tmp_path,
        playbook_manager,
        status_reporter,
        security_scanner,
        iac_generator,
    )

    async def fake_tests(self, workflow_id, playbook_id):
        return WorkflowPhaseResult(
            name="testing",
            status="completed",
            started_at="stub",
            completed_at="stub",
            details={"stub": True},
        )

    engine._run_tests = fake_tests.__get__(engine, ModernizationWorkflowEngine)

    result = await engine.run_workflow(workflow_name="pytest-stub")

    assert result["status"] == "completed"
    assert status_reporter.workflow_events, "Expected workflow events recorded"
    assert (tmp_path / "assets").exists(), "IaC generator should emit artifacts"
    persisted = status_reporter.event_store_path
    assert persisted and persisted.exists(), "Workflow events should persist to disk"

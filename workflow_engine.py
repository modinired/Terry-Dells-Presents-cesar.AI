"""Modernization workflow orchestration for Terry Super Ecosystem."""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .playbook_manager import PlaybookManager
from ..utils.logger import setup_logger
from ..utils.security_scanner import SecurityScanner
from ..utils.iac_generator import IaCGenerator


@dataclass
class WorkflowPhaseResult:
    name: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class ModernizationWorkflowEngine:
    """Coordinate assessment, remediation, validation, and deployment phases."""

    def __init__(
        self,
        project_root: Path,
        playbooks: PlaybookManager,
        status_reporter,
        security_scanner: SecurityScanner,
        iac_generator: IaCGenerator,
    ) -> None:
        self.project_root = project_root
        self.playbooks = playbooks
        self.status_reporter = status_reporter
        self.security_scanner = security_scanner
        self.iac_generator = iac_generator
        self.logger = setup_logger("workflow_engine")
        self._workflows: Dict[str, Dict[str, Any]] = {}

    def list_workflows(self) -> List[Dict[str, Any]]:
        return list(self._workflows.values())

    async def run_workflow(
        self,
        *,
        playbook_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        workflow_id = str(uuid.uuid4())
        workflow_name = workflow_name or f"modernization-{workflow_id[:8]}"
        record = {
            "workflow_id": workflow_id,
            "name": workflow_name,
            "playbook_id": playbook_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "phases": [],
            "status": "in_progress",
        }
        self._workflows[workflow_id] = record
        await self._push_update(workflow_id, "workflow", "started", record)

        try:
            phases = [
                ("assessment", self._run_assessment),
                ("remediation", self._run_remediation),
                ("testing", self._run_tests),
                ("security", self._run_security),
                ("deployment", self._run_deployment),
            ]

            for phase_name, handler in phases:
                phase_result = await handler(workflow_id, playbook_id)
                record["phases"].append(phase_result)
                await self._push_update(workflow_id, phase_name, phase_result.status, phase_result.details)
                if phase_result.status not in {"completed", "skipped"}:
                    record["status"] = "blocked"
                    break

            if record["status"] == "in_progress":
                record["status"] = "completed"

        except Exception as exc:  # pragma: no cover - defensive path
            self.logger.exception("Workflow execution failed", exc_info=exc)
            record["status"] = "failed"
            await self._push_update(
                workflow_id,
                "workflow",
                "failed",
                {"error": str(exc)},
            )

        self._workflows[workflow_id] = record
        await self._push_update(workflow_id, "workflow", record["status"], record)
        return record

    async def _run_assessment(self, workflow_id: str, playbook_id: Optional[str]) -> WorkflowPhaseResult:
        started = datetime.utcnow().isoformat()
        assessment = self.playbooks.assess_project(self.project_root)
        if playbook_id:
            assessment["playbook_preview"] = self.playbooks.apply_playbook(playbook_id, self.project_root)
        completed = datetime.utcnow().isoformat()
        return WorkflowPhaseResult(
            name="assessment",
            status="completed",
            started_at=started,
            completed_at=completed,
            details=assessment,
        )

    async def _run_remediation(self, workflow_id: str, playbook_id: Optional[str]) -> WorkflowPhaseResult:
        started = datetime.utcnow().isoformat()
        results: Dict[str, Any] = {"applied_playbook": playbook_id, "actions": []}
        if playbook_id:
            try:
                results["actions"] = self.playbooks.apply_playbook(playbook_id, self.project_root)["results"]
                status = "completed"
            except Exception as exc:
                status = "blocked"
                results["error"] = str(exc)
        else:
            status = "skipped"
        completed = datetime.utcnow().isoformat()
        return WorkflowPhaseResult(
            name="remediation",
            status=status,
            started_at=started,
            completed_at=completed,
            details=results,
        )

    async def _run_tests(self, workflow_id: str, playbook_id: Optional[str]) -> WorkflowPhaseResult:
        started = datetime.utcnow().isoformat()
        cmd = ["python3", "-m", "pytest", "-q"]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        status = "completed" if process.returncode == 0 else "blocked"
        completed = datetime.utcnow().isoformat()
        return WorkflowPhaseResult(
            name="testing",
            status=status,
            started_at=started,
            completed_at=completed,
            details={
                "return_code": process.returncode,
                "stdout": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
            },
        )

    async def _run_security(self, workflow_id: str, playbook_id: Optional[str]) -> WorkflowPhaseResult:
        started = datetime.utcnow().isoformat()
        scan_results = await self.security_scanner.run_scans(self.project_root)
        status = "completed" if scan_results.get("status") == "ok" else "blocked"
        completed = datetime.utcnow().isoformat()
        return WorkflowPhaseResult(
            name="security",
            status=status,
            started_at=started,
            completed_at=completed,
            details=scan_results,
        )

    async def _run_deployment(self, workflow_id: str, playbook_id: Optional[str]) -> WorkflowPhaseResult:
        started = datetime.utcnow().isoformat()
        artifacts = self.iac_generator.generate_bundle(
            bundle_name=f"{workflow_id[:8]}-bundle",
            project_root=self.project_root,
            metadata={"playbook_id": playbook_id},
        )
        completed = datetime.utcnow().isoformat()
        return WorkflowPhaseResult(
            name="deployment",
            status="completed",
            started_at=started,
            completed_at=completed,
            artifacts=artifacts,
        )

    async def _push_update(self, workflow_id: str, phase: str, status: str, payload: Dict[str, Any]) -> None:
        if hasattr(self.status_reporter, "record_workflow_update"):
            await self.status_reporter.record_workflow_update(
                workflow_id,
                phase,
                status,
                payload,
            )


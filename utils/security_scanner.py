"""Security scanning helpers for modernization workflows."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from .logger import setup_logger


class SecurityScanner:
    """Aggregate security checks (dependency, secrets, container)."""

    def __init__(self) -> None:
        self.logger = setup_logger("security_scanner")

    async def run_scans(self, project_root: Path) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []

        dep = await self._run_pip_audit(project_root)
        checks.append(dep)

        secret = await self._scan_for_secrets(project_root)
        checks.append(secret)

        status = "ok" if all(check.get("status") == "ok" for check in checks) else "attention"
        return {"status": status, "checks": checks}

    async def _run_pip_audit(self, project_root: Path) -> Dict[str, Any]:
        if shutil.which("pip-audit") is None:
            self.logger.warning("pip-audit not installed; skipping dependency scan")
            return {"tool": "pip-audit", "status": "skipped", "reason": "missing"}

        process = await asyncio.create_subprocess_exec(
            "pip-audit",
            "--format",
            "json",
            cwd=str(project_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            self.logger.warning("pip-audit exited with %s", process.returncode)
            return {
                "tool": "pip-audit",
                "status": "attention",
                "return_code": process.returncode,
                "stderr": stderr.decode().strip(),
            }

        try:
            payload = json.loads(stdout.decode() or "[]")
        except json.JSONDecodeError as exc:
            self.logger.warning("Failed to parse pip-audit output: %s", exc)
            payload = []
        vulnerabilities = [item for item in payload if item.get("vulns")]
        return {
            "tool": "pip-audit",
            "status": "ok" if not vulnerabilities else "attention",
            "results": payload,
        }

    async def _scan_for_secrets(self, project_root: Path) -> Dict[str, Any]:
        suspicious: List[str] = []
        for path in project_root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if "SECRET_KEY" in text or "AWS_ACCESS_KEY_ID" in text:
                suspicious.append(str(path.relative_to(project_root)))
        status = "ok" if not suspicious else "attention"
        return {"tool": "heuristic-secret-scan", "status": status, "findings": suspicious}


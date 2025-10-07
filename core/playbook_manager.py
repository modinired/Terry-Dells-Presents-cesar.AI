"""Management of modernization playbooks and custom automation formulas."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..playbooks import PREDEFINED_PLAYBOOKS
from ..utils.logger import setup_logger


@dataclass
class Playbook:
    """Serializable representation of a modernization playbook."""

    identifier: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    origin: str = "predefined"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identifier": self.identifier,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "steps": self.steps,
            "metadata": self.metadata,
            "origin": self.origin,
        }


class PlaybookManager:
    """Central registry for modernization playbooks and automation templates."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.custom_dir = self.root_dir / "playbooks" / "custom"
        self.logger = setup_logger("playbook_manager")
        self._playbooks: Dict[str, Playbook] = {}
        self._load_predefined()
        self._load_custom()

    def _load_predefined(self) -> None:
        for entry in PREDEFINED_PLAYBOOKS:
            playbook = Playbook(**entry, origin="predefined")
            self._playbooks[playbook.identifier] = playbook
        self.logger.info("Loaded %d predefined playbooks", len(PREDEFINED_PLAYBOOKS))

    def _load_custom(self) -> None:
        if not self.custom_dir.exists():
            return
        for item in self.custom_dir.glob("*.json"):
            try:
                data = json.loads(item.read_text())
                playbook = Playbook(**data, origin="custom")
                self._playbooks[playbook.identifier] = playbook
            except Exception as exc:
                self.logger.warning("Failed to load custom playbook %s: %s", item, exc)

    def list_playbooks(self, *, tags: Optional[Iterable[str]] = None) -> List[Dict[str, Any]]:
        if not tags:
            return [p.to_dict() for p in self._playbooks.values()]
        tag_set = {tag.lower() for tag in tags}
        return [
            p.to_dict()
            for p in self._playbooks.values()
            if tag_set.intersection({t.lower() for t in p.tags})
        ]

    def get_playbook(self, identifier: str) -> Optional[Playbook]:
        return self._playbooks.get(identifier)

    def assess_project(self, project_root: Path) -> Dict[str, Any]:
        """Perform lightweight assessment mirroring Copilot's modernization assessment."""

        requirement_files = list(project_root.glob("**/requirements*.txt"))
        outdated_candidates: List[str] = []
        secrets_found: List[str] = []

        for req_file in requirement_files:
            for line in req_file.read_text().splitlines():
                normalized = line.strip()
                if not normalized or normalized.startswith("#"):
                    continue
                if any(token in normalized.lower() for token in ["password", "secret", "key"]):
                    secrets_found.append(f"{req_file.name}:{normalized}")
                if "==" in normalized:
                    outdated_candidates.append(normalized)

        cicd_files = list(project_root.glob(".github/workflows/*.yml"))

        assessment = {
            "requirements_files": [str(f.relative_to(project_root)) for f in requirement_files],
            "hardcoded_secret_suspects": secrets_found,
            "pin_candidates": outdated_candidates,
            "cicd_workflows_detected": [str(f.relative_to(project_root)) for f in cicd_files],
        }

        self.logger.info(
            "Assessment complete: %d requirements, %d suspect secrets",
            len(requirement_files),
            len(secrets_found),
        )
        return assessment

    def save_custom_playbook(self, playbook: Playbook) -> Path:
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        target = self.custom_dir / f"{playbook.identifier}.json"
        target.write_text(json.dumps(playbook.to_dict(), indent=2))
        self._playbooks[playbook.identifier] = playbook
        self.logger.info("Custom playbook saved to %s", target)
        return target

    def create_custom_playbook_from_diff(
        self,
        name: str,
        description: str,
        *,
        labels: Optional[List[str]] = None,
        commits: Optional[List[str]] = None,
        include_working_tree: bool = False,
    ) -> Playbook:
        """Generate a custom playbook by capturing git diffs as repeatable steps."""

        diff_payload = self._collect_diff(commits=commits, working=include_working_tree)
        identifier = self._normalize_identifier(name)
        playbook = Playbook(
            identifier=identifier,
            name=name,
            description=description,
            tags=labels or ["custom"],
            steps=[
                {
                    "action": "apply_patch",
                    "name": "Replay captured git diff",
                    "details": "Apply the stored diff onto a target repository.",
                    "payload": diff_payload,
                }
            ],
            metadata={"source_commits": commits or [], "has_working_tree": include_working_tree},
            origin="custom",
        )
        self.save_custom_playbook(playbook)
        return playbook

    def _collect_diff(
        self,
        *,
        commits: Optional[List[str]] = None,
        working: bool = False,
    ) -> str:
        args: List[str]
        if commits and len(commits) == 2:
            args = ["git", "diff", commits[0], commits[1]]
        elif commits:
            args = ["git", "diff", commits[0]]
        else:
            args = ["git", "diff"]
        if not working:
            args.append("--cached")

        try:
            completed = subprocess.run(
                args,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                self.logger.warning("git diff exited with %s", completed.returncode)
            return completed.stdout.strip()
        except FileNotFoundError:
            self.logger.error("git executable not available; returning empty diff")
            return ""

    def _normalize_identifier(self, name: str) -> str:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name)
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-")

    def apply_playbook(self, identifier: str, target_dir: Path) -> Dict[str, Any]:
        playbook = self.get_playbook(identifier)
        if not playbook:
            raise ValueError(f"Unknown playbook: {identifier}")

        results: List[Dict[str, Any]] = []
        for step in playbook.steps:
            action = step.get("action")
            handler = getattr(self, f"_handle_{action}", None)
            if not handler:
                results.append({"step": step.get("name"), "status": "skipped", "reason": "unsupported"})
                continue
            results.append(handler(step, target_dir))
        return {"playbook": identifier, "results": results}

    def _handle_apply_patch(self, step: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        patch_content = step.get("payload", "")
        if not patch_content:
            return {"status": "skipped", "reason": "empty diff"}

        patch_file = target_dir / "_playbook_patch.diff"
        patch_file.write_text(patch_content)
        return {
            "status": "generated",
            "artifact": str(patch_file.relative_to(self.root_dir)),
            "message": "Diff written for manual or automated application.",
        }

    def _handle_scan(self, step: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        # Mirror scanning by reusing assessment capabilities.
        assessment = self.assess_project(target_dir)
        return {"status": "completed", "data": assessment}

    def _handle_plan(self, step: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        plan = {
            "status": "completed",
            "recommendations": step.get("details"),
            "artifacts": [],
        }
        return plan

    def _handle_transform(self, step: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        # Placeholder: real implementation would invoke agents.
        return {
            "status": "pending_review",
            "message": "Transformations require agent execution or manual review.",
        }

    def _handle_verify(self, step: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        return {
            "status": "queued",
            "message": "Verification delegated to workflow testing phase.",
        }

    def _handle_configure(self, step: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        return {
            "status": "generated",
            "message": step.get("details", ""),
        }

    def _handle_validate(self, step: Dict[str, Any], target_dir: Path) -> Dict[str, Any]:
        return {
            "status": "queued",
            "message": "Load validation handled by workflow engine.",
        }


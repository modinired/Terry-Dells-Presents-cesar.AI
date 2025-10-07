"""Infrastructure-as-code asset generator for modernization workflows."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .logger import setup_logger


class IaCGenerator:
    """Produce container and CI/CD assets inspired by Copilot modernization."""

    def __init__(self, output_root: Path) -> None:
        self.output_root = output_root
        self.logger = setup_logger("iac_generator")
        self.output_root.mkdir(parents=True, exist_ok=True)

    def generate_bundle(self, *, bundle_name: str, project_root: Path, metadata: Dict[str, str]) -> List[str]:
        bundle_dir = self.output_root / bundle_name
        bundle_dir.mkdir(parents=True, exist_ok=True)

        artifacts: List[str] = []
        artifacts.append(self._write_dockerfile(bundle_dir))
        artifacts.append(self._write_compose(bundle_dir))
        artifacts.append(self._write_github_actions(bundle_dir, metadata))
        artifacts.append(self._write_metadata(bundle_dir, metadata, project_root))

        self.logger.info("IaC bundle %s generated with %d artifacts", bundle_name, len(artifacts))
        return [str(Path(artifact).relative_to(self.output_root)) for artifact in artifacts]

    def _write_dockerfile(self, bundle_dir: Path) -> Path:
        dockerfile = bundle_dir / "Dockerfile"
        dockerfile.write_text(
            "# Generated Terry modernization Dockerfile\n"
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY . /app\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "CMD [\"python\", \"-m\", \"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
        )
        return dockerfile

    def _write_compose(self, bundle_dir: Path) -> Path:
        compose = bundle_dir / "docker-compose.yml"
        compose.write_text(
            "version: '3.9'\n"
            "services:\n"
            "  app:\n"
            "    build: .\n"
            "    ports:\n"
            "      - '8000:8000'\n"
            "    environment:\n"
            "      - ENV=production\n"
            "    depends_on:\n"
            "      - postgres\n"
            "  postgres:\n"
            "    image: postgres:15\n"
            "    restart: always\n"
            "    environment:\n"
            "      POSTGRES_PASSWORD: changeme\n"
            "    volumes:\n"
            "      - postgres-data:/var/lib/postgresql/data\n"
            "volumes:\n"
            "  postgres-data:\n"
        )
        return compose

    def _write_github_actions(self, bundle_dir: Path, metadata: Dict[str, str]) -> Path:
        workflow_dir = bundle_dir / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        workflow = workflow_dir / "modernization-ci.yml"
        workflow.write_text(
            "name: Terry Modernization CI\n"
            "on:\n"
            "  push:\n"
            "    branches: [ main ]\n"
            "  pull_request:\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.11'\n"
            "      - run: pip install -r requirements.txt\n"
            "      - run: pytest\n"
            "      - run: pip install pip-audit && pip-audit\n"
            "      - run: docker build -t terry-modernized .\n"
        )
        return workflow

    def _write_metadata(self, bundle_dir: Path, metadata: Dict[str, str], project_root: Path) -> Path:
        manifest = bundle_dir / "bundle.json"
        manifest.write_text(
            json.dumps(
                {
                    "generated_at": datetime.utcnow().isoformat(),
                    "project_root": str(project_root),
                    "metadata": metadata,
                },
                indent=2,
            )
        )
        return manifest

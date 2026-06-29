"""File-backed JSON persistence for the Sprint 2 vertical slice."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStore:
    """Small deterministic JSON store used by local API, CLI, and tests."""

    def __init__(self, root: str | Path = ".genesis-data") -> None:
        self.root = Path(root)
        self.projects_dir = self.root / "projects"
        self.workflows_dir = self.root / "workflows"
        self.employee_outputs_dir = self.root / "employee_outputs"
        self.reports_dir = self.root / "reports"
        for directory in [self.projects_dir, self.workflows_dir, self.employee_outputs_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def save_project(self, project: dict[str, Any]) -> None:
        self._write(self.projects_dir / f"{project['id']}.json", project)

    def get_project(self, project_id: str) -> dict[str, Any]:
        return self._read(self.projects_dir / f"{project_id}.json")

    def save_workflow(self, workflow: dict[str, Any]) -> None:
        self._write(self.workflows_dir / f"{workflow['id']}.json", workflow)

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._read(self.workflows_dir / f"{workflow_id}.json")

    def save_employee_output(self, output: dict[str, Any]) -> None:
        filename = f"{output['workflowId']}__{output['employeeId']}.json"
        self._write(self.employee_outputs_dir / filename, output)

    def list_employee_outputs(self, workflow_id: str) -> list[dict[str, Any]]:
        return [self._read(path) for path in sorted(self.employee_outputs_dir.glob(f"{workflow_id}__*.json"))]

    def save_report(self, report: dict[str, Any]) -> None:
        self._write(self.reports_dir / f"{report['projectId']}.json", report)

    def get_report(self, project_id: str) -> dict[str, Any]:
        return self._read(self.reports_dir / f"{project_id}.json")

    def _write(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _read(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Genesis store record not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

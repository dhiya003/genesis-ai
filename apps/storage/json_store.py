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
        self.approvals_dir = self.root / "approvals"
        self.metrics_dir = self.root / "metrics"
        self.tasks_dir = self.root / "tasks"
        self.deliverables_dir = self.root / "deliverables"
        self.audit_logs_dir = self.root / "audit_logs"
        self.execution_history_dir = self.root / "execution_history"
        self.product_definitions_dir = self.root / "product_definitions"
        self.product_knowledge_dir = self.root / "product_knowledge"
        for directory in [
            self.projects_dir,
            self.workflows_dir,
            self.employee_outputs_dir,
            self.reports_dir,
            self.approvals_dir,
            self.metrics_dir,
            self.tasks_dir,
            self.deliverables_dir,
            self.audit_logs_dir,
            self.execution_history_dir,
            self.product_definitions_dir,
            self.product_knowledge_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def save_project(self, project: dict[str, Any]) -> None:
        self._write(self.projects_dir / f"{project['id']}.json", project)

    def get_project(self, project_id: str) -> dict[str, Any]:
        return self._read(self.projects_dir / f"{project_id}.json")

    def save_workflow(self, workflow: dict[str, Any]) -> None:
        self._write(self.workflows_dir / f"{workflow['id']}.json", workflow)

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._read(self.workflows_dir / f"{workflow_id}.json")

    def list_workflows(self, status: str | None = None) -> list[dict[str, Any]]:
        workflows = [self._read(path) for path in sorted(self.workflows_dir.glob("*.json"))]
        if status is None:
            return workflows
        return [workflow for workflow in workflows if workflow.get("status") == status]

    def save_employee_output(self, output: dict[str, Any]) -> None:
        filename = f"{output['workflowId']}__{output['employeeId']}.json"
        self._write(self.employee_outputs_dir / filename, output)

    def list_employee_outputs(self, workflow_id: str) -> list[dict[str, Any]]:
        return [self._read(path) for path in sorted(self.employee_outputs_dir.glob(f"{workflow_id}__*.json"))]

    def save_report(self, report: dict[str, Any]) -> None:
        self._write(self.reports_dir / f"{report['projectId']}.json", report)

    def get_report(self, project_id: str) -> dict[str, Any]:
        return self._read(self.reports_dir / f"{project_id}.json")

    def save_approval(self, approval: dict[str, Any]) -> None:
        self._write(self.approvals_dir / f"{approval['id']}.json", approval)

    def get_approval(self, approval_id: str) -> dict[str, Any]:
        return self._read(self.approvals_dir / f"{approval_id}.json")

    def list_approvals(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        approvals = [self._read(path) for path in sorted(self.approvals_dir.glob("*.json"))]
        if project_id is not None:
            approvals = [approval for approval in approvals if approval.get("projectId") == project_id]
        if workflow_id is not None:
            approvals = [approval for approval in approvals if approval.get("workflowId") == workflow_id]
        return approvals

    def save_metric(self, metric: dict[str, Any]) -> None:
        self._write(self.metrics_dir / f"{metric['id']}.json", metric)

    def list_metrics(self, limit: int | None = None) -> list[dict[str, Any]]:
        metrics = [self._read(path) for path in sorted(self.metrics_dir.glob("*.json"))]
        metrics.sort(key=lambda item: str(item.get("createdAt", "")))
        if limit is None:
            return metrics
        return metrics[-limit:]

    def save_task(self, task: dict[str, Any]) -> None:
        self._write(self.tasks_dir / f"{task['id']}.json", task)

    def list_tasks(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        tasks = [self._read(path) for path in sorted(self.tasks_dir.glob("*.json"))]
        if project_id is not None:
            tasks = [task for task in tasks if task.get("projectId") == project_id]
        if workflow_id is not None:
            tasks = [task for task in tasks if task.get("workflowId") == workflow_id]
        return tasks

    def save_deliverable(self, deliverable: dict[str, Any]) -> None:
        self._write(self.deliverables_dir / f"{deliverable['id']}.json", deliverable)

    def list_deliverables(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        deliverables = [self._read(path) for path in sorted(self.deliverables_dir.glob("*.json"))]
        if project_id is not None:
            deliverables = [deliverable for deliverable in deliverables if deliverable.get("projectId") == project_id]
        if workflow_id is not None:
            deliverables = [deliverable for deliverable in deliverables if deliverable.get("workflowId") == workflow_id]
        return deliverables

    def save_audit_log(self, audit_log: dict[str, Any]) -> None:
        self._write(self.audit_logs_dir / f"{audit_log['id']}.json", audit_log)

    def list_audit_logs(self, project_id: str | None = None, workflow_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        audit_logs = [self._read(path) for path in sorted(self.audit_logs_dir.glob("*.json"))]
        if project_id is not None:
            audit_logs = [audit_log for audit_log in audit_logs if audit_log.get("projectId") == project_id]
        if workflow_id is not None:
            audit_logs = [audit_log for audit_log in audit_logs if audit_log.get("workflowId") == workflow_id]
        audit_logs.sort(key=lambda item: str(item.get("createdAt", "")))
        if limit is None:
            return audit_logs
        return audit_logs[-limit:]

    def save_execution_event(self, event: dict[str, Any]) -> None:
        self._write(self.execution_history_dir / f"{event['id']}.json", event)

    def list_execution_history(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        events = [self._read(path) for path in sorted(self.execution_history_dir.glob("*.json"))]
        if project_id is not None:
            events = [event for event in events if event.get("projectId") == project_id]
        if workflow_id is not None:
            events = [event for event in events if event.get("workflowId") == workflow_id]
        events.sort(key=lambda item: str(item.get("createdAt", "")))
        return events

    def save_product_definition(self, product_definition: dict[str, Any]) -> None:
        self._write(self.product_definitions_dir / f"{product_definition['projectId']}.json", product_definition)

    def get_product_definition(self, project_id: str) -> dict[str, Any]:
        return self._read(self.product_definitions_dir / f"{project_id}.json")

    def save_product_knowledge(self, entry: dict[str, Any]) -> None:
        project_id = entry["projectId"]
        existing = self.list_product_knowledge(project_id=project_id)
        sequence = len(existing) + 1
        self._write(self.product_knowledge_dir / f"{project_id}__{sequence:03d}.json", entry)

    def list_product_knowledge(self, project_id: str | None = None) -> list[dict[str, Any]]:
        entries = [self._read(path) for path in sorted(self.product_knowledge_dir.glob("*.json"))]
        if project_id is not None:
            entries = [entry for entry in entries if entry.get("projectId") == project_id]
        return entries

    def _write(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _read(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Genesis store record not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

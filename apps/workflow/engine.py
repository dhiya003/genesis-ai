"""Workflow state engine for Sprint 2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from time import perf_counter
from typing import Any, Callable
from uuid import uuid4

from apps.audit import record_audit, record_execution_event
from apps.observability import MetricsRecorder
from apps.storage import JsonStore

WorkflowStep = Callable[[dict[str, Any]], dict[str, Any]]
LOGGER = logging.getLogger("genesis.workflow")
WORKFLOW_STATES = {"NEW", "PLANNING", "RUNNING", "WAITING", "COMPLETED", "FAILED", "RETRYING", "CANCELLED"}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass
class WorkflowEngine:
    """Create, run, complete, fail, and retry workflows."""

    store: JsonStore

    def create(self, project_id: str, workflow_type: str) -> dict[str, Any]:
        workflow = {
            "id": str(uuid4()),
            "projectId": project_id,
            "type": workflow_type,
            "status": "NEW",
            "attempt": 1,
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
            "error": None,
            "stateHistory": [{"status": "NEW", "at": now_iso(), "reason": "workflow created"}],
        }
        self.store.save_workflow(workflow)
        MetricsRecorder(self.store).record("workflow.created", {"status": "NEW", "type": workflow_type}, project_id=project_id, workflow_id=workflow["id"])
        record_audit(self.store, "workflow.created", project_id=project_id, workflow_id=workflow["id"], details={"type": workflow_type})
        record_execution_event(self.store, "workflow.created", project_id=project_id, workflow_id=workflow["id"], status="NEW")
        LOGGER.info("workflow created", extra={"event": "workflow.created", "project_id": project_id, "workflow_id": workflow["id"], "status": "NEW"})
        return workflow

    def plan(self, workflow: dict[str, Any], reason: str = "workflow planning started") -> dict[str, Any]:
        return self._transition(workflow, "PLANNING", reason=reason, metric_type="workflow.planning")

    def run(self, workflow: dict[str, Any], step: WorkflowStep) -> dict[str, Any]:
        workflow = dict(workflow)
        if workflow["status"] not in {"NEW", "PLANNING", "RETRYING"}:
            raise ValueError(f"Workflow must be NEW, PLANNING, or RETRYING before run; got {workflow['status']}")
        workflow = self._transition(workflow, "RUNNING", reason="workflow execution started", metric_type="workflow.running")
        started = perf_counter()
        LOGGER.info("workflow running", extra={"event": "workflow.running", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "RUNNING"})
        try:
            result = step(workflow)
        except Exception as exc:  # noqa: BLE001
            return self.fail(workflow, str(exc), runtime_seconds=perf_counter() - started)
        return self.complete(workflow, result, runtime_seconds=perf_counter() - started)

    def complete(self, workflow: dict[str, Any], result: dict[str, Any], runtime_seconds: float | None = None) -> dict[str, Any]:
        workflow = dict(workflow)
        workflow["status"] = "COMPLETED"
        workflow["result"] = result
        workflow["error"] = None
        workflow = self._transition(workflow, "COMPLETED", reason="workflow completed")
        values: dict[str, Any] = {"attempt": workflow["attempt"], "status": "COMPLETED"}
        if runtime_seconds is not None:
            values["runtimeSeconds"] = round(runtime_seconds, 4)
        MetricsRecorder(self.store).record("workflow.completed", values, project_id=workflow["projectId"], workflow_id=workflow["id"])
        LOGGER.info("workflow completed", extra={"event": "workflow.completed", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return workflow

    def fail(self, workflow: dict[str, Any], error: str, runtime_seconds: float | None = None) -> dict[str, Any]:
        workflow = dict(workflow)
        workflow["error"] = {"message": error, "failedAt": now_iso()}
        workflow = self._transition(workflow, "FAILED", reason=error)
        values: dict[str, Any] = {"attempt": workflow["attempt"], "status": "FAILED", "error": error}
        if runtime_seconds is not None:
            values["runtimeSeconds"] = round(runtime_seconds, 4)
        MetricsRecorder(self.store).record("workflow.failed", values, project_id=workflow["projectId"], workflow_id=workflow["id"])
        LOGGER.info("workflow failed", extra={"event": "workflow.failed", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "FAILED"})
        return workflow

    def retry(self, workflow_id: str) -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        if workflow["status"] != "FAILED":
            raise ValueError("Only FAILED workflows can be retried")
        workflow = dict(workflow)
        workflow["attempt"] += 1
        workflow["error"] = None
        workflow = self._transition(workflow, "RETRYING", reason="workflow retry requested", metric_type="workflow.retried")
        LOGGER.info("workflow retried", extra={"event": "workflow.retried", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "RETRYING"})
        return workflow

    def pause(self, workflow_id: str, reason: str = "workflow paused") -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        if workflow["status"] not in {"NEW", "PLANNING", "RUNNING", "RETRYING"}:
            raise ValueError("Only active workflows can be paused")
        return self._transition(workflow, "WAITING", reason=reason, metric_type="workflow.paused")

    def cancel(self, workflow_id: str, reason: str = "workflow cancelled") -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        if workflow["status"] in {"COMPLETED", "CANCELLED"}:
            raise ValueError("Only incomplete workflows can be cancelled")
        return self._transition(workflow, "CANCELLED", reason=reason, metric_type="workflow.cancelled")

    def resume(self, workflow_id: str, step: WorkflowStep) -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        if workflow["status"] == "COMPLETED":
            return workflow
        if workflow["status"] == "FAILED":
            workflow = self.retry(workflow_id)
        elif workflow["status"] == "WAITING":
            workflow = self._transition(workflow, "PLANNING", reason="paused workflow resumed", metric_type="workflow.resumed")
        elif workflow["status"] == "RUNNING":
            workflow = dict(workflow)
            workflow["attempt"] += 1
            workflow["recoveredFrom"] = "RUNNING"
            workflow = self._transition(workflow, "RETRYING", reason="interrupted running workflow recovered")
            MetricsRecorder(self.store).record("workflow.recovered", {"attempt": workflow["attempt"], "fromStatus": "RUNNING"}, project_id=workflow["projectId"], workflow_id=workflow["id"])
        elif workflow["status"] == "NEW":
            workflow = self.plan(workflow, reason="new workflow resumed into planning")
        elif workflow["status"] not in {"PLANNING", "RETRYING"}:
            raise ValueError("Only NEW, PLANNING, WAITING, RUNNING, FAILED, RETRYING, or COMPLETED workflows can be resumed")
        return self.run(workflow, step)

    def _transition(self, workflow: dict[str, Any], status: str, *, reason: str, metric_type: str | None = None) -> dict[str, Any]:
        if status not in WORKFLOW_STATES:
            raise ValueError(f"Unknown workflow status: {status}")
        workflow = dict(workflow)
        previous = workflow.get("status")
        timestamp = now_iso()
        workflow["status"] = status
        workflow["updatedAt"] = timestamp
        history = list(workflow.get("stateHistory", []))
        history.append({"from": previous, "status": status, "at": timestamp, "reason": reason})
        workflow["stateHistory"] = history
        self.store.save_workflow(workflow)
        if metric_type:
            MetricsRecorder(self.store).record(metric_type, {"attempt": workflow["attempt"], "status": status, "fromStatus": previous}, project_id=workflow["projectId"], workflow_id=workflow["id"])
        record_audit(self.store, f"workflow.{status.lower()}", project_id=workflow["projectId"], workflow_id=workflow["id"], details={"fromStatus": previous, "reason": reason})
        record_execution_event(self.store, f"workflow.{status.lower()}", project_id=workflow["projectId"], workflow_id=workflow["id"], status=status, details={"fromStatus": previous, "reason": reason})
        return workflow

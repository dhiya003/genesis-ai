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
WORKFLOW_STATES = {"NEW", "VALIDATING", "PLANNING", "READY", "RUNNING", "WAITING", "APPROVAL_REQUIRED", "RESUMING", "COMPLETED", "FAILED", "RETRYING", "CANCELLED", "ARCHIVED"}
VALID_WORKFLOW_TRANSITIONS = {
    "NEW": {"VALIDATING", "PLANNING", "READY", "RUNNING", "WAITING", "CANCELLED", "ARCHIVED"},
    "VALIDATING": {"PLANNING", "READY", "FAILED", "CANCELLED"},
    "PLANNING": {"READY", "RUNNING", "WAITING", "FAILED", "CANCELLED"},
    "READY": {"RUNNING", "WAITING", "FAILED", "CANCELLED"},
    "RUNNING": {"WAITING", "APPROVAL_REQUIRED", "COMPLETED", "FAILED", "RETRYING", "CANCELLED"},
    "WAITING": {"RESUMING", "PLANNING", "READY", "RUNNING", "CANCELLED"},
    "APPROVAL_REQUIRED": {"RESUMING", "PLANNING", "RUNNING", "COMPLETED", "CANCELLED"},
    "RESUMING": {"PLANNING", "READY", "RUNNING", "RETRYING", "FAILED", "CANCELLED"},
    "FAILED": {"RETRYING", "CANCELLED", "ARCHIVED"},
    "RETRYING": {"RUNNING", "WAITING", "FAILED", "CANCELLED"},
    "COMPLETED": {"ARCHIVED"},
    "CANCELLED": {"ARCHIVED"},
    "ARCHIVED": set(),
}


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass
class WorkflowEngine:
    """Create, run, complete, fail, and retry workflows."""

    store: JsonStore

    def create(
        self,
        project_id: str,
        workflow_type: str,
        *,
        created_by: str = "system",
        name: str | None = None,
        priority: str = "MEDIUM",
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        if idempotency_key:
            for existing in self.store.list_workflows():
                if existing.get("projectId") == project_id and existing.get("idempotencyKey") == idempotency_key:
                    return existing
        business_id = None
        try:
            business_id = self.store.get_project(project_id).get("businessId")
        except FileNotFoundError:
            business_id = None
        workflow = {
            "id": str(uuid4()),
            "name": name or f"{workflow_type.title().replace('_', ' ')} Workflow",
            "projectId": project_id,
            "businessId": business_id,
            "type": workflow_type,
            "status": "NEW",
            "currentStage": "NEW",
            "currentDepartment": None,
            "currentEmployee": None,
            "estimatedDurationSeconds": None,
            "actualDurationSeconds": None,
            "progressPercent": 0,
            "version": 1,
            "createdBy": created_by,
            "priority": priority,
            "idempotencyKey": idempotency_key,
            "attempt": 1,
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
            "error": None,
            "stateHistory": [{"status": "NEW", "at": now_iso(), "reason": "workflow created"}],
            "eventsPublished": ["workflow.created"],
        }
        self.store.save_workflow(workflow)
        MetricsRecorder(self.store).record("workflow.created", {"status": "NEW", "type": workflow_type}, project_id=project_id, workflow_id=workflow["id"])
        record_audit(self.store, "workflow.created", project_id=project_id, workflow_id=workflow["id"], details={"type": workflow_type})
        record_execution_event(self.store, "workflow.created", project_id=project_id, workflow_id=workflow["id"], status="NEW")
        self._notify(workflow, "workflow.started", "Workflow created and ready for planning.")
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
        workflow["result"] = result
        workflow["error"] = None
        if runtime_seconds is not None:
            workflow["actualDurationSeconds"] = round(runtime_seconds, 4)
        workflow["progressPercent"] = 100
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
        if runtime_seconds is not None:
            workflow["actualDurationSeconds"] = round(runtime_seconds, 4)
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
            workflow = self._transition(workflow, "RESUMING", reason="paused workflow resumed", metric_type="workflow.resumed")
            workflow = self._transition(workflow, "PLANNING", reason="resumed workflow returned to planning")
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

    def progress(self, workflow_id: str) -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        tasks = self.store.list_tasks(workflow_id=workflow_id)
        outputs = self.store.list_employee_outputs(workflow_id)
        deliverables = self.store.list_deliverables(workflow_id=workflow_id)
        completed_tasks = [task for task in tasks if task.get("status") == "COMPLETED"]
        failed_tasks = [task for task in tasks if task.get("status") == "FAILED"]
        task_progress = round((len(completed_tasks) / len(tasks)) * 100) if tasks else int(workflow.get("progressPercent", 0))
        return {
            "workflow": workflow,
            "currentPhase": workflow.get("currentStage", workflow.get("status")),
            "currentDepartment": workflow.get("currentDepartment") or workflow.get("scheduledDepartment"),
            "currentEmployee": workflow.get("currentEmployee"),
            "completedTasks": completed_tasks,
            "remainingTasks": [task for task in tasks if task.get("status") not in {"COMPLETED", "FAILED"}],
            "estimatedCompletion": workflow.get("estimatedCompletion"),
            "elapsedSeconds": workflow.get("actualDurationSeconds"),
            "progressPercent": max(int(workflow.get("progressPercent", 0)), task_progress),
            "blockingIssues": failed_tasks + ([workflow["error"]] if workflow.get("error") else []),
            "warnings": [] if workflow.get("status") not in {"WAITING", "APPROVAL_REQUIRED"} else [f"Workflow is {workflow['status']}"],
            "employeeOutputs": outputs,
            "deliverables": deliverables,
        }

    def history(self, workflow_id: str) -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        return {
            "workflow": workflow,
            "stateHistory": workflow.get("stateHistory", []),
            "executionHistory": self.store.list_execution_history(workflow_id=workflow_id),
            "employees": self.store.list_employee_outputs(workflow_id),
            "deliverables": self.store.list_deliverables(workflow_id=workflow_id),
            "approvals": self.store.list_approvals(workflow_id=workflow_id),
            "notifications": self.store.list_workflow_notifications(workflow_id=workflow_id),
            "export": {"format": "json"},
        }

    def notifications(self, workflow_id: str) -> dict[str, Any]:
        return {"workflowId": workflow_id, "notifications": self.store.list_workflow_notifications(workflow_id=workflow_id), "configurable": True}

    def _transition(self, workflow: dict[str, Any], status: str, *, reason: str, metric_type: str | None = None) -> dict[str, Any]:
        if status not in WORKFLOW_STATES:
            raise ValueError(f"Unknown workflow status: {status}")
        workflow = dict(workflow)
        previous = workflow.get("status")
        if previous != status and status not in VALID_WORKFLOW_TRANSITIONS.get(str(previous), set()):
            raise ValueError(f"Invalid workflow transition from {previous} to {status}")
        timestamp = now_iso()
        workflow["status"] = status
        workflow["currentStage"] = status
        workflow["updatedAt"] = timestamp
        history = list(workflow.get("stateHistory", []))
        history.append({"from": previous, "status": status, "at": timestamp, "reason": reason})
        workflow["stateHistory"] = history
        events = list(workflow.get("eventsPublished", []))
        event_type = f"workflow.{status.lower()}"
        events.append(event_type)
        workflow["eventsPublished"] = events
        self.store.save_workflow(workflow)
        if metric_type:
            MetricsRecorder(self.store).record(metric_type, {"attempt": workflow["attempt"], "status": status, "fromStatus": previous}, project_id=workflow["projectId"], workflow_id=workflow["id"])
        record_audit(self.store, event_type, project_id=workflow["projectId"], workflow_id=workflow["id"], details={"fromStatus": previous, "reason": reason})
        record_execution_event(self.store, event_type, project_id=workflow["projectId"], workflow_id=workflow["id"], status=status, details={"fromStatus": previous, "reason": reason})
        self._notify(workflow, event_type, _notification_message(status, reason))
        return workflow

    def _notify(self, workflow: dict[str, Any], event_type: str, message: str) -> None:
        dedupe_key = f"{event_type}__{workflow.get('attempt', 1)}__{workflow.get('status')}".replace("/", "_")
        notification = {
            "id": str(uuid4()),
            "workflowId": workflow["id"],
            "projectId": workflow["projectId"],
            "businessId": workflow.get("businessId"),
            "type": event_type,
            "message": message,
            "status": workflow.get("status"),
            "dedupeKey": dedupe_key,
            "createdAt": now_iso(),
        }
        self.store.save_workflow_notification(notification)


def _notification_message(status: str, reason: str) -> str:
    messages = {
        "RUNNING": "Workflow execution started.",
        "COMPLETED": "Workflow completed successfully.",
        "FAILED": "Workflow failed and may require retry.",
        "RETRYING": "Workflow retry started.",
        "WAITING": "Workflow paused or waiting.",
        "CANCELLED": "Workflow cancelled.",
        "APPROVAL_REQUIRED": "Workflow requires founder approval.",
        "RESUMING": "Workflow resume started.",
    }
    return f"{messages.get(status, f'Workflow moved to {status}.')} Reason: {reason}"

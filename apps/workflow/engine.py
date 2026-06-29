"""Workflow state engine for Sprint 2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from typing import Any, Callable
from uuid import uuid4

from apps.storage import JsonStore

WorkflowStep = Callable[[dict[str, Any]], dict[str, Any]]
LOGGER = logging.getLogger("genesis.workflow")


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
            "status": "CREATED",
            "attempt": 1,
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
            "error": None,
        }
        self.store.save_workflow(workflow)
        LOGGER.info("workflow created", extra={"event": "workflow.created", "project_id": project_id, "workflow_id": workflow["id"], "status": "CREATED"})
        return workflow

    def run(self, workflow: dict[str, Any], step: WorkflowStep) -> dict[str, Any]:
        workflow = dict(workflow)
        workflow["status"] = "RUNNING"
        workflow["updatedAt"] = now_iso()
        self.store.save_workflow(workflow)
        LOGGER.info("workflow running", extra={"event": "workflow.running", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "RUNNING"})
        try:
            result = step(workflow)
        except Exception as exc:  # noqa: BLE001
            return self.fail(workflow, str(exc))
        return self.complete(workflow, result)

    def complete(self, workflow: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        workflow = dict(workflow)
        workflow["status"] = "COMPLETED"
        workflow["result"] = result
        workflow["error"] = None
        workflow["updatedAt"] = now_iso()
        self.store.save_workflow(workflow)
        LOGGER.info("workflow completed", extra={"event": "workflow.completed", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return workflow

    def fail(self, workflow: dict[str, Any], error: str) -> dict[str, Any]:
        workflow = dict(workflow)
        workflow["status"] = "FAILED"
        workflow["error"] = {"message": error, "failedAt": now_iso()}
        workflow["updatedAt"] = now_iso()
        self.store.save_workflow(workflow)
        LOGGER.info("workflow failed", extra={"event": "workflow.failed", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "FAILED"})
        return workflow

    def retry(self, workflow_id: str) -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        if workflow["status"] != "FAILED":
            raise ValueError("Only FAILED workflows can be retried")
        workflow["status"] = "CREATED"
        workflow["attempt"] += 1
        workflow["error"] = None
        workflow["updatedAt"] = now_iso()
        self.store.save_workflow(workflow)
        LOGGER.info("workflow retried", extra={"event": "workflow.retried", "project_id": workflow["projectId"], "workflow_id": workflow["id"], "status": "CREATED"})
        return workflow

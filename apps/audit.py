"""Audit and execution history helpers for Genesis runtime events."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from apps.storage import JsonStore


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def record_audit(
    store: JsonStore,
    event: str,
    *,
    project_id: str | None = None,
    workflow_id: str | None = None,
    actor: str = "genesis",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    audit_log = {
        "id": str(uuid4()),
        "event": event,
        "actor": actor,
        "projectId": project_id,
        "workflowId": workflow_id,
        "details": details or {},
        "createdAt": now_iso(),
    }
    store.save_audit_log(audit_log)
    return audit_log


def record_execution_event(
    store: JsonStore,
    event: str,
    *,
    project_id: str | None = None,
    workflow_id: str | None = None,
    status: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    execution_event = {
        "id": str(uuid4()),
        "event": event,
        "status": status,
        "projectId": project_id,
        "workflowId": workflow_id,
        "details": details or {},
        "createdAt": now_iso(),
    }
    store.save_execution_event(execution_event)
    return execution_event

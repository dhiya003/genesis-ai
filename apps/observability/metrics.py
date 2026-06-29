"""Simple persisted runtime metrics for local observability."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from apps.storage import JsonStore


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class MetricsRecorder:
    """Records workflow, employee, API, and recovery metrics to the JSON store."""

    store: JsonStore

    def record(self, metric_type: str, values: dict[str, Any], *, project_id: str | None = None, workflow_id: str | None = None) -> dict[str, Any]:
        metric = {
            "id": str(uuid4()),
            "type": metric_type,
            "projectId": project_id,
            "workflowId": workflow_id,
            "values": values,
            "createdAt": _now_iso(),
        }
        self.store.save_metric(metric)
        return metric

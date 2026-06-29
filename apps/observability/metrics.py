"""Simple persisted runtime metrics for local observability."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import mean
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


def summarize_metrics(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a compact operational summary from persisted metric events."""

    workflow_durations = _numbers(metrics, "workflow.completed", "runtimeSeconds")
    employee_durations = _numbers(metrics, "employee.completed", "runtimeSeconds")
    confidence_levels = [
        str(metric.get("values", {}).get("confidence"))
        for metric in metrics
        if metric.get("type") == "research.report_stored" and metric.get("values", {}).get("confidence")
    ]
    provider_usage = [metric for metric in metrics if str(metric.get("type", "")).startswith("provider.")]
    search_metrics = [metric for metric in metrics if str(metric.get("type", "")).startswith("search.")]
    errors = [metric for metric in metrics if str(metric.get("type", "")).endswith(".failed")]
    return {
        "eventCount": len(metrics),
        "workflowDuration": _summary_stats(workflow_durations),
        "employeeDuration": _summary_stats(employee_durations),
        "providerUsageEvents": len(provider_usage),
        "searchEvents": len(search_metrics),
        "errorCount": len(errors),
        "confidenceDistribution": {level: confidence_levels.count(level) for level in sorted(set(confidence_levels))},
    }


def _numbers(metrics: list[dict[str, Any]], metric_type: str, key: str) -> list[float]:
    values = []
    for metric in metrics:
        if metric.get("type") != metric_type:
            continue
        value = metric.get("values", {}).get(key)
        if isinstance(value, int | float):
            values.append(float(value))
    return values


def _summary_stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "avg": None, "max": None}
    return {"count": len(values), "avg": round(mean(values), 4), "max": round(max(values), 4)}

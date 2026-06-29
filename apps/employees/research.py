"""Executable Genesis AI research employee modules."""

from __future__ import annotations

from typing import Any

from apps.research.providers import ResearchProvider, get_research_provider

EMPLOYEES = ["EMP-001", "EMP-002", "EMP-003", "EMP-004"]


def run_employee(employee_id: str, project: dict[str, Any], provider: ResearchProvider | None = None) -> dict[str, Any]:
    """Execute one research employee and normalize the persisted output."""

    if employee_id not in EMPLOYEES:
        raise ValueError(f"Unknown research employee: {employee_id}")
    active_provider = provider or get_research_provider()
    output = active_provider.run(employee_id, project["idea"])
    output.update({
        "employeeId": employee_id,
        "projectId": project["id"],
        "workflowId": project["workflowId"],
        "status": "COMPLETED",
    })
    return output

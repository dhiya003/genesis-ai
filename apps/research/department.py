"""Research Department vertical-slice execution."""

from __future__ import annotations

import logging
from statistics import mean
from typing import Any

from apps.employees import EMPLOYEES, run_employee
from apps.storage import JsonStore
from scripts.validate_research_report import validate_research_report_payload

LOGGER = logging.getLogger("genesis.research")


class ResearchDepartment:
    """Executes EMP-001 to EMP-004 and combines their outputs."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def execute(self, project: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
        project_context = dict(project)
        project_context["workflowId"] = workflow["id"]
        outputs = []
        LOGGER.info("research department started", extra={"event": "research.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        for employee_id in EMPLOYEES:
            LOGGER.info("employee execution started", extra={"event": "employee.started", "project_id": project["id"], "workflow_id": workflow["id"], "employee_id": employee_id, "status": "RUNNING"})
            output = run_employee(employee_id, project_context)
            self.store.save_employee_output(output)
            outputs.append(output)
            LOGGER.info("employee execution completed", extra={"event": "employee.completed", "project_id": project["id"], "workflow_id": workflow["id"], "employee_id": employee_id, "status": "COMPLETED"})
        report = self.combine(project_context, workflow, outputs)
        validation_issues = validate_research_report_payload(report)
        if validation_issues:
            raise ValueError(f"Research report validation failed: {validation_issues}")
        self.store.save_report(report)
        LOGGER.info("research report stored", extra={"event": "research.report_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return report

    def combine(self, project: dict[str, Any], workflow: dict[str, Any], outputs: list[dict[str, Any]]) -> dict[str, Any]:
        by_section = {output["section"]: output for output in outputs}
        overall_score = round(mean(output["score"] for output in outputs))
        return {
            "reportType": "RESEARCH_REPORT",
            "projectId": project["id"],
            "workflowId": workflow["id"],
            "idea": project["idea"],
            "overallScore": overall_score,
            "trendAnalysis": by_section["trendAnalysis"],
            "competitorAnalysis": by_section["competitorAnalysis"],
            "customerAnalysis": by_section["customerAnalysis"],
            "productResearch": by_section["productResearch"],
            "recommendation": _recommendation(overall_score),
            "risks": [
                "Competitor saturation must be verified with live marketplace and Instagram checks.",
                "The first offer may fail if it looks like generic merchandise.",
                "Unit economics must include packaging, shipping, and damaged-return risk.",
            ],
            "nextActions": [
                "Check 10 India coffee/gifting competitors and record prices.",
                "Create one starter kit mockup and publish an interest post.",
                "Collect 5 serious customer conversations before buying inventory.",
            ],
        }


def _recommendation(score: int) -> str:
    if score >= 75:
        return "Proceed with a lean manual validation launch before investing in inventory or ads."
    if score >= 60:
        return "Proceed only after narrowing the target customer and improving differentiation."
    return "Do not proceed yet; gather stronger customer demand evidence first."

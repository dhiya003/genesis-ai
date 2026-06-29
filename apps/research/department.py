"""Research Department vertical-slice execution."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

from apps.employees import EMPLOYEES, run_employee
from apps.observability import MetricsRecorder
from apps.research.intelligence import CitationEngine, ConfidenceEngine, CostTracker, collect_parallel
from apps.storage import JsonStore
from scripts.validate_research_report import validate_research_report_payload

LOGGER = logging.getLogger("genesis.research")


class ResearchDepartment:
    """Executes EMP-001 to EMP-004 and combines their outputs."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store
        self.confidence_engine = ConfidenceEngine()
        self.citation_engine = CitationEngine()
        self.cost_tracker = CostTracker()

    def execute(self, project: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
        project_context = dict(project)
        project_context["workflowId"] = workflow["id"]
        LOGGER.info("research department started", extra={"event": "research.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})

        def execute_employee(employee_id: str) -> dict[str, Any]:
            LOGGER.info("employee execution started", extra={"event": "employee.started", "project_id": project["id"], "workflow_id": workflow["id"], "employee_id": employee_id, "status": "RUNNING"})
            started = perf_counter()
            output = run_employee(employee_id, project_context)
            self.store.save_employee_output(output)
            MetricsRecorder(self.store).record(
                "employee.completed",
                {"employeeId": employee_id, "runtimeSeconds": round(perf_counter() - started, 4), "score": output.get("score")},
                project_id=project["id"],
                workflow_id=workflow["id"],
            )
            LOGGER.info("employee execution completed", extra={"event": "employee.completed", "project_id": project["id"], "workflow_id": workflow["id"], "employee_id": employee_id, "status": "COMPLETED"})
            return output

        outputs = collect_parallel(EMPLOYEES, execute_employee)
        report = self.combine(project_context, workflow, outputs)
        validation_issues = validate_research_report_payload(report)
        if validation_issues:
            raise ValueError(f"Research report validation failed: {validation_issues}")
        self.store.save_report(report)
        MetricsRecorder(self.store).record(
            "research.report_stored",
            {"overallScore": report["overallScore"], "confidence": report.get("confidence", {}).get("level")},
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("research report stored", extra={"event": "research.report_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return report

    def combine(self, project: dict[str, Any], workflow: dict[str, Any], outputs: list[dict[str, Any]]) -> dict[str, Any]:
        by_section = {output["section"]: output for output in outputs}
        overall_score = round(mean(output["score"] for output in outputs))
        evidence = _collect_evidence(outputs)
        confidence = self.confidence_engine.score(evidence)
        citations = self.citation_engine.build(evidence)
        self.cost_tracker.record("research_department", {"employees": len(outputs), "evidenceItems": len(evidence)})
        recommendation = _recommendation(overall_score, confidence)
        risks = [
            "Competitor saturation must be verified with live marketplace and Instagram checks.",
            "The first offer may fail if it looks like generic merchandise.",
            "Unit economics must include packaging, shipping, and damaged-return risk.",
        ]
        next_actions = [
            "Check 10 India coffee/gifting competitors and record prices.",
            "Create one starter kit mockup and publish an interest post.",
            "Collect 5 serious customer conversations before buying inventory.",
        ]
        return {
            "reportType": "RESEARCH_REPORT",
            "projectId": project["id"],
            "workflowId": workflow["id"],
            "idea": project["idea"],
            "executiveSummary": f"Genesis Research Department evaluated '{project['idea']}' using EMP-001 to EMP-004 and recommends: {recommendation}",
            "overallScore": overall_score,
            "opportunityScore": overall_score,
            "confidence": confidence,
            "evidence": evidence,
            "citations": citations,
            "costSummary": self.cost_tracker.summary(),
            "trendAnalysis": by_section["trendAnalysis"],
            "competitorAnalysis": by_section["competitorAnalysis"],
            "customerAnalysis": by_section["customerAnalysis"],
            "productResearch": by_section["productResearch"],
            "productAnalysis": by_section["productResearch"],
            "recommendation": recommendation,
            "recommendations": [recommendation],
            "risks": risks,
            "nextActions": next_actions,
        }


def _collect_evidence(outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for output in outputs:
        section = output.get("section")
        for item in output.get("evidence", []):
            normalized = dict(item)
            normalized.setdefault("section", section)
            evidence.append(normalized)
    return evidence


def _recommendation(score: int, confidence: dict[str, Any] | None = None) -> str:
    confidence_level = (confidence or {}).get("level", "LOW")
    if score >= 75 and confidence_level in {"HIGH", "MEDIUM"}:
        return "Proceed with a lean manual validation launch before investing in inventory or ads."
    if score >= 75:
        return "Promising, but proceed only after improving evidence confidence with live customer and competitor checks."
    if score >= 60:
        return "Proceed only after narrowing the target customer and improving differentiation."
    return "Do not proceed yet; gather stronger customer demand evidence first."

#!/usr/bin/env python3
"""Validate a Genesis Sprint 2 research report using strict stdlib checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "projectId",
    "workflowId",
    "idea",
    "executiveSummary",
    "trendAnalysis",
    "competitorAnalysis",
    "customerAnalysis",
    "productAnalysis",
    "productResearch",
    "overallScore",
    "opportunityScore",
    "opportunityRating",
    "opportunityScoring",
    "confidence",
    "evidence",
    "recommendation",
    "recommendations",
    "executiveRecommendation",
    "risks",
    "riskAssessment",
    "nextActions",
    "citations",
    "mergeSummary",
    "researchExecution",
    "completionChecklist",
    "downstreamReadiness",
]

EMPLOYEE_SECTIONS = {
    "trendAnalysis": "EMP-001",
    "competitorAnalysis": "EMP-002",
    "customerAnalysis": "EMP-003",
    "productResearch": "EMP-004",
}


def validate_research_report_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "RESEARCH_REPORT":
        issues.append("reportType must be RESEARCH_REPORT")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be a number from 0 to 100")
    opportunity_score = data.get("opportunityScore")
    if not isinstance(opportunity_score, (int, float)) or not 0 <= opportunity_score <= 100:
        issues.append("opportunityScore must be a number from 0 to 100")
    if data.get("opportunityRating") not in {"Very Poor", "Poor", "Average", "Good", "Excellent"}:
        issues.append("opportunityRating must be one of Very Poor, Poor, Average, Good, or Excellent")
    opportunity_scoring = data.get("opportunityScoring")
    if not isinstance(opportunity_scoring, dict) or not isinstance(opportunity_scoring.get("weights"), dict) or not opportunity_scoring.get("explanation"):
        issues.append("opportunityScoring must include weights and explanation")
    confidence = data.get("confidence")
    if not isinstance(confidence, dict) or confidence.get("level") not in {"LOW", "MEDIUM", "HIGH"}:
        issues.append("confidence.level must be LOW, MEDIUM, or HIGH")
    for key in ["evidence", "citations", "recommendations"]:
        if not isinstance(data.get(key), list):
            issues.append(f"{key} must be a list")
    for key in ["risks", "nextActions"]:
        if not isinstance(data.get(key), list) or not data.get(key):
            issues.append(f"{key} must be a non-empty list")
    risk_assessment = data.get("riskAssessment")
    if not isinstance(risk_assessment, list) or len(risk_assessment) < 4:
        issues.append("riskAssessment must include categorized risks")
    else:
        for index, risk in enumerate(risk_assessment):
            if not isinstance(risk, dict):
                issues.append(f"riskAssessment[{index}] must be an object")
                continue
            for key in ["category", "severity", "likelihood", "mitigation", "evidence"]:
                if key not in risk:
                    issues.append(f"riskAssessment[{index}].{key} is required")
    executive = data.get("executiveRecommendation")
    if not isinstance(executive, dict) or executive.get("type") not in {"Proceed", "Proceed with Caution", "Validate Further", "Pivot", "Do Not Proceed"}:
        issues.append("executiveRecommendation.type must be a supported recommendation type")
    execution = data.get("researchExecution")
    if not isinstance(execution, dict) or not execution.get("parallelExecutionSupported") or not execution.get("sequentialFallbackSupported"):
        issues.append("researchExecution must document parallel support and sequential fallback")
    checklist = data.get("completionChecklist")
    if not isinstance(checklist, list) or not checklist or any(item.get("status") != "PASS" for item in checklist if isinstance(item, dict)):
        issues.append("completionChecklist must contain passing checklist items")
    downstream = data.get("downstreamReadiness")
    if not isinstance(downstream, dict) or downstream.get("productFactoryInputReady") is not True:
        issues.append("downstreamReadiness.productFactoryInputReady must be true")
    for section, expected_employee in EMPLOYEE_SECTIONS.items():
        value = data.get(section)
        if not isinstance(value, dict):
            issues.append(f"{section} must be an object")
            continue
        if value.get("employeeId") != expected_employee:
            issues.append(f"{section}.employeeId must be {expected_employee}")
        if value.get("section") != section:
            issues.append(f"{section}.section must be {section}")
        section_score = value.get("score")
        if not isinstance(section_score, (int, float)) or not 0 <= section_score <= 100:
            issues.append(f"{section}.score must be a number from 0 to 100")
        if not value.get("summary"):
            issues.append(f"{section}.summary is required")
        if not value.get("evidence"):
            issues.append(f"{section}.evidence is required")
        if not isinstance(value.get("confidence"), dict):
            issues.append(f"{section}.confidence is required")
        validation = value.get("validation")
        if not isinstance(validation, dict) or any(validation.get(key) != "PASS" for key in ["schema", "evidence", "confidence", "status"]):
            issues.append(f"{section}.validation must pass schema, evidence, confidence, and status")
    return issues


def validate_research_report(path: Path) -> list[str]:
    return validate_research_report_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-research-report-v2.json")
    issues = validate_research_report(path)
    if issues:
        print("FAIL: research report validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis research report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

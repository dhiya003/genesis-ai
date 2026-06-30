#!/usr/bin/env python3
"""Validate a Genesis Sprint 8 Business Operating Plan."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "projectId",
    "businessId",
    "launchId",
    "workflowId",
    "department",
    "runtime",
    "founderVision",
    "executiveCouncil",
    "departmentPlans",
    "crossDepartmentLoop",
    "strategicPlan",
    "businessPlan",
    "digitalTwin",
    "knowledgeGraph",
    "businessMemory",
    "portfolioPlan",
    "resourcePlan",
    "decisionRegister",
    "approvalPolicy",
    "simulationResults",
    "businessHealth",
    "opportunities",
    "risks",
    "recommendations",
    "learningEngine",
    "selfImprovementPlan",
    "integrationRegistry",
    "dashboards",
    "observabilityPlan",
    "securityPlan",
    "governanceBoundaries",
    "nextActions",
    "overallScore",
]


def validate_business_operating_plan_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "BUSINESS_OPERATING_PLAN":
        issues.append("reportType must be BUSINESS_OPERATING_PLAN")
    if data.get("department") != "BUSINESS_OS":
        issues.append("department must be BUSINESS_OS")
    if not data.get("executiveCouncil"):
        issues.append("executiveCouncil is required")
    if not data.get("departmentPlans"):
        issues.append("departmentPlans is required")
    if "Research Again" not in data.get("crossDepartmentLoop", []):
        issues.append("crossDepartmentLoop must include Research Again")
    if not data.get("decisionRegister"):
        issues.append("decisionRegister is required")
    for decision in data.get("decisionRegister", []):
        if not all(key in decision for key in ["decision", "reason", "evidence", "confidence", "risk", "alternatives", "expectedOutcome", "approvalRequirement"]):
            issues.append("each decision must include reason, evidence, confidence, risk, alternatives, expectedOutcome, and approvalRequirement")
            break
    twin = data.get("digitalTwin", {})
    for key in ["products", "inventory", "customers", "marketing", "sales", "operations", "finance", "goals", "kpis", "currentState"]:
        if key not in twin:
            issues.append(f"digitalTwin.{key} is required")
    graph = data.get("knowledgeGraph", {})
    if not graph.get("nodes") or not graph.get("edges"):
        issues.append("knowledgeGraph nodes and edges are required")
    health = data.get("businessHealth", {})
    if not isinstance(health.get("overallBusinessHealthScore"), (int, float)) or not 0 <= health.get("overallBusinessHealthScore", -1) <= 100:
        issues.append("businessHealth.overallBusinessHealthScore must be 0-100")
    if not data.get("simulationResults"):
        issues.append("simulationResults is required")
    if not data.get("recommendations"):
        issues.append("recommendations is required")
    if not data.get("approvalPolicy", {}).get("manual"):
        issues.append("approvalPolicy.manual is required")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_business_operating_plan(path: Path) -> list[str]:
    return validate_business_operating_plan_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-business-operating-plan.json")
    issues = validate_business_operating_plan(path)
    if issues:
        print("FAIL: business operating plan validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis business operating plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

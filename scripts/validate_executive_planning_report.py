#!/usr/bin/env python3
"""Validate a Genesis v2 Executive Planning Report."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "businessId",
    "projectId",
    "workflowId",
    "executivePlanningEngine",
    "annualBusinessPlan",
    "quarterlyObjectives",
    "weeklyExecutionPlan",
    "resourceAllocation",
    "initiativePrioritization",
    "strategicConflicts",
    "executiveActionPlan",
    "executiveReview",
    "decisionRegisterUpdated",
    "completionChecklist",
    "completionStatus",
    "overallScore",
]


def validate_executive_planning_report_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "EXECUTIVE_PLANNING_REPORT":
        issues.append("reportType must be EXECUTIVE_PLANNING_REPORT")
    engine = data.get("executivePlanningEngine", {})
    for key in ["initialized", "businessContextLoaded", "organizationalMemoryConnected", "executiveCouncilConnected", "dashboardUpdated", "auditRecorded"]:
        if engine.get(key) is not True:
            issues.append(f"executivePlanningEngine.{key} must be true")
    annual = data.get("annualBusinessPlan", {})
    for key in ["generated", "financialTargetsIncluded", "departmentObjectivesAligned", "milestonesIdentified", "risksDocumented", "versionControlled"]:
        if annual.get(key) is not True:
            issues.append(f"annualBusinessPlan.{key} must be true")
    okrs = data.get("quarterlyObjectives", {})
    for key in ["objectivesMeasurable", "keyResultsDefined", "departmentOwnershipAssigned", "progressTrackingEnabled", "dependenciesIdentified"]:
        if okrs.get(key) is not True:
            issues.append(f"quarterlyObjectives.{key} must be true")
    weekly = data.get("weeklyExecutionPlan", {})
    for key in ["generated", "tasksPrioritized", "bottlenecksIdentified", "resourceConflictsDetected", "timelineGenerated"]:
        if weekly.get(key) is not True:
            issues.append(f"weeklyExecutionPlan.{key} must be true")
    resources = data.get("resourceAllocation", {})
    for key in ["calculated", "conflictsHighlighted", "overallocationPrevented", "tradeOffsExplained", "recommendationsGenerated"]:
        if resources.get(key) is not True:
            issues.append(f"resourceAllocation.{key} must be true")
    initiatives = data.get("initiativePrioritization", {})
    for key in ["ranked", "scoringExplained", "supportingEvidenceLinked", "alternativePrioritiesSuggested"]:
        if initiatives.get(key) is not True:
            issues.append(f"initiativePrioritization.{key} must be true")
    conflicts = data.get("strategicConflicts", {})
    for key in ["conflictsIdentified", "severityAssigned", "departmentsAffectedListed", "resolutionRecommendationsGenerated"]:
        if conflicts.get(key) is not True:
            issues.append(f"strategicConflicts.{key} must be true")
    action = data.get("executiveActionPlan", {})
    for key in ["strategyDecomposedIntoActions", "departmentOwnershipAssigned", "milestonesDefined", "successMetricsIncluded", "dependenciesLinked"]:
        if action.get(key) is not True:
            issues.append(f"executiveActionPlan.{key} must be true")
    review = data.get("executiveReview", {})
    for key in ["generated", "departmentSummariesIncluded", "strategicActionsProposed", "decisionRegisterUpdated", "founderApprovalRequestedWhereRequired"]:
        if review.get(key) is not True:
            issues.append(f"executiveReview.{key} must be true")
    status = data.get("completionStatus", {})
    for key in ["executivePlanningMarkedComplete", "plansAvailableAcrossDepartments", "executiveDashboardUpdated", "organizationalMemoryUpdated", "futurePlanningReferencesPreviousPlans", "founderNotified"]:
        if status.get(key) is not True:
            issues.append(f"completionStatus.{key} must be true")
    if data.get("decisionRegisterUpdated") is not True:
        issues.append("decisionRegisterUpdated must be true")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_executive_planning_report(path: Path) -> list[str]:
    return validate_executive_planning_report_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0] if argv else sys.argv[1] if len(sys.argv) > 1 else "testing/fixtures/sample-executive-planning-report.json")
    issues = validate_executive_planning_report(path)
    if issues:
        print("FAIL: executive planning report validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis executive planning report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

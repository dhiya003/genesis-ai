#!/usr/bin/env python3
"""Validate a Genesis v2 Execution Optimization Report."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED = ["reportType", "businessId", "workflowId", "optimizationEngine", "workflowOptimization", "employeeOptimization", "promptOptimization", "resourceOptimization", "recommendationOptimization", "collaborationOptimization", "selfEvaluation", "executiveOptimizationReport", "adaptiveGovernanceBoundary", "completionStatus", "overallScore"]


def validate_execution_optimization_report_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = [f"missing top-level key: {key}" for key in REQUIRED if key not in data]
    if data.get("reportType") != "EXECUTION_OPTIMIZATION_REPORT":
        issues.append("reportType must be EXECUTION_OPTIMIZATION_REPORT")
    engine = data.get("optimizationEngine", {})
    for key in ["initialized", "historicalDataLoaded", "organizationalMemoryConnected", "knowledgeGraphConnected", "executiveDashboardUpdated", "auditCreated"]:
        if engine.get(key) is not True:
            issues.append(f"optimizationEngine.{key} must be true")
    checks = {
        "workflowOptimization": ["bottlenecksDetected", "improvementSuggestionsGenerated", "historicalComparisonAvailable", "expectedImpactEstimated", "founderApprovalRequiredForGovernedChanges"],
        "employeeOptimization": ["performanceMeasured", "weakPerformersIdentified", "improvementOpportunitiesGenerated", "metricsStored", "historicalTrendsAvailable"],
        "promptOptimization": ["promptVersionsCompared", "performanceMetricsStored", "preferredPromptsIdentified", "rollbackSupported", "changeHistoryPreserved"],
        "resourceOptimization": ["resourceUtilizationAnalyzed", "conflictsDetected", "wasteIdentified", "optimizationRecommendationsGenerated", "tradeOffsExplained"],
        "recommendationOptimization": ["recommendationQualityMeasured", "predictionAccuracyTracked", "weakRecommendationPatternsIdentified", "confidenceRecalibrated"],
        "collaborationOptimization": ["knowledgeShared", "duplicateWorkReduced", "handoffsImproved", "crossDepartmentMetricsAvailable"],
        "selfEvaluation": ["evaluationScheduleSupported", "evaluationReportsGenerated", "weaknessesIdentified", "improvementBacklogGenerated"],
    }
    for section, keys in checks.items():
        for key in keys:
            if data.get(section, {}).get(key) is not True:
                issues.append(f"{section}.{key} must be true")
    report = data.get("executiveOptimizationReport", {})
    for key in ["generated", "versionControlled", "historicalComparisonAvailable", "dashboardUpdated", "knowledgeStored"]:
        if report.get(key) is not True:
            issues.append(f"executiveOptimizationReport.{key} must be true")
    boundary = data.get("adaptiveGovernanceBoundary", {})
    if boundary.get("governanceRulesProtected") is not True or boundary.get("adaptiveIntelligenceAllowed") is not True:
        issues.append("adaptiveGovernanceBoundary must protect governance while allowing adaptive intelligence")
    status = data.get("completionStatus", {})
    for key in ["optimizationCycleCompleted", "recommendationsEvidenceBacked", "governedChangesNotAppliedAutomatically", "improvementHistoryPreserved", "executiveCouncilNotified", "founderReceivesSummary", "learningAvailableForFutureExecution"]:
        if status.get(key) is not True:
            issues.append(f"completionStatus.{key} must be true")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_execution_optimization_report(path: Path) -> list[str]:
    return validate_execution_optimization_report_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0] if argv else sys.argv[1] if len(sys.argv) > 1 else "testing/fixtures/sample-execution-optimization-report.json")
    issues = validate_execution_optimization_report(path)
    if issues:
        print("FAIL: execution optimization report validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis execution optimization report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

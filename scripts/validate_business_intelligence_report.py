#!/usr/bin/env python3
"""Validate a Genesis Sprint 7 Business Intelligence Report."""

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
    "departmentStatus",
    "businessIntelligenceDepartment",
    "chiefBusinessAnalyst",
    "monitoringPlan",
    "dashboardUpdate",
    "auditSummary",
    "metricsCollection",
    "salesAnalytics",
    "marketingAnalytics",
    "customerAnalytics",
    "productPerformanceAnalytics",
    "businessHealth",
    "recommendations",
    "executiveBusinessReport",
    "completionChecklist",
    "founderNotification",
    "workflowTransition",
    "departmentMetrics",
    "knowledgeBaseEntries",
    "overallScore",
]


def validate_business_intelligence_report_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "BUSINESS_INTELLIGENCE_REPORT":
        issues.append("reportType must be BUSINESS_INTELLIGENCE_REPORT")
    if data.get("department") != "BUSINESS_INTELLIGENCE":
        issues.append("department must be BUSINESS_INTELLIGENCE")
    if data.get("departmentStatus") != "COMPLETED":
        issues.append("departmentStatus must be COMPLETED")
    if not data.get("chiefBusinessAnalyst"):
        issues.append("chiefBusinessAnalyst is required")
    if data.get("businessIntelligenceDepartment", {}).get("businessConnected") is not True:
        issues.append("businessIntelligenceDepartment.businessConnected must be true")
    metrics = data.get("metricsCollection", {})
    for key in ["collected", "dataSources", "metrics", "duplicateHandling", "missingDataFlags", "collectionHistory", "timestampRecorded"]:
        if key not in metrics or not metrics.get(key):
            issues.append(f"metricsCollection.{key} is required")
    if not data.get("salesAnalytics", {}).get("reportsStored"):
        issues.append("salesAnalytics.reportsStored must be true")
    if not data.get("marketingAnalytics", {}).get("campaignComparison"):
        issues.append("marketingAnalytics.campaignComparison is required")
    if not data.get("customerAnalytics", {}).get("customerSegments"):
        issues.append("customerAnalytics.customerSegments is required")
    if data.get("productPerformanceAnalytics", {}).get("productRankingGenerated") is not True:
        issues.append("productPerformanceAnalytics.productRankingGenerated must be true")
    health = data.get("businessHealth", {})
    if not isinstance(health.get("score"), (int, float)) or not 0 <= health.get("score", -1) <= 100:
        issues.append("businessHealth.score must be 0-100")
    for key in ["healthRating", "explanation", "trends", "historicalComparison"]:
        if not health.get(key):
            issues.append(f"businessHealth.{key} is required")
    recommendations = data.get("recommendations", [])
    if not recommendations:
        issues.append("recommendations are required")
    for recommendation in recommendations:
        if not all(key in recommendation for key in ["recommendation", "priority", "expectedImpact", "confidence", "evidence"]):
            issues.append("each recommendation must include priority, expectedImpact, confidence, and evidence")
            break
    report = data.get("executiveBusinessReport", {})
    for key in ["executiveSummary", "kpiDashboard", "businessHealth", "salesAnalysis", "marketingAnalysis", "customerAnalysis", "productAnalysis", "risks", "opportunities", "recommendations", "nextActions"]:
        if not report.get(key):
            issues.append(f"executiveBusinessReport.{key} is required")
    for key in ["versionControlled", "downloadable", "searchable", "linkedToProject"]:
        if report.get(key) is not True:
            issues.append(f"executiveBusinessReport.{key} must be true")
    if data.get("workflowTransition") != "BUSINESS_OPERATING_SYSTEM":
        issues.append("workflowTransition must be BUSINESS_OPERATING_SYSTEM")
    for key in ["completionChecklist", "departmentMetrics", "knowledgeBaseEntries", "auditSummary"]:
        if not data.get(key):
            issues.append(f"{key} is required")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_business_intelligence_report(path: Path) -> list[str]:
    return validate_business_intelligence_report_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-business-intelligence-report.json")
    issues = validate_business_intelligence_report(path)
    if issues:
        print("FAIL: business intelligence report validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis business intelligence report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

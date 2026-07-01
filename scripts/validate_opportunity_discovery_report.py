#!/usr/bin/env python3
"""Validate a Genesis v2 Opportunity Discovery Report."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED = ["reportType", "businessId", "workflowId", "discoveryEngine", "productOpportunities", "marketOpportunities", "competitorWeaknesses", "customerNeeds", "pricingOpportunities", "supplierOpportunities", "growthOpportunities", "executiveOpportunityReport", "opportunityPipeline", "completionStatus", "overallScore"]


def validate_opportunity_discovery_report_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = [f"missing top-level key: {key}" for key in REQUIRED if key not in data]
    if data.get("reportType") != "OPPORTUNITY_DISCOVERY_REPORT":
        issues.append("reportType must be OPPORTUNITY_DISCOVERY_REPORT")
    engine = data.get("discoveryEngine", {})
    for key in ["initialized", "monitoringScheduleCreated", "dataSourcesConnected", "discoveryHistoryMaintained", "dashboardUpdated", "auditRecorded"]:
        if engine.get(key) is not True:
            issues.append(f"discoveryEngine.{key} must be true")
    for key in ["productOpportunities", "marketOpportunities", "competitorWeaknesses", "customerNeeds", "pricingOpportunities", "supplierOpportunities", "growthOpportunities"]:
        if not data.get(key):
            issues.append(f"{key} is required")
    report = data.get("executiveOpportunityReport", {})
    for key in ["generated", "versionControlled", "searchable", "downloadable", "linkedToBusinessMemory", "opportunityHistoryPreserved"]:
        if report.get(key) is not True:
            issues.append(f"executiveOpportunityReport.{key} must be true")
    status = data.get("completionStatus", {})
    for key in ["departmentCompleted", "opportunityPipelineCreated", "futureMonitoringScheduled", "executiveCouncilNotified", "founderNotified", "recommendationsStored", "knowledgeAvailableForFuturePlanning"]:
        if status.get(key) is not True:
            issues.append(f"completionStatus.{key} must be true")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_opportunity_discovery_report(path: Path) -> list[str]:
    return validate_opportunity_discovery_report_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0] if argv else sys.argv[1] if len(sys.argv) > 1 else "testing/fixtures/sample-opportunity-discovery-report.json")
    issues = validate_opportunity_discovery_report(path)
    if issues:
        print("FAIL: opportunity discovery report validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis opportunity discovery report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

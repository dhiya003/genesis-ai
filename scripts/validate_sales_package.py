#!/usr/bin/env python3
"""Validate a Genesis Sprint 6 Sales Package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "projectId",
    "salesId",
    "marketingId",
    "creativeId",
    "productId",
    "workflowId",
    "department",
    "departmentStatus",
    "salesDepartment",
    "salesDirector",
    "salesExecutionPlan",
    "communicationChannels",
    "marketingPackageLoaded",
    "departmentVisibleInWorkflow",
    "leadQualification",
    "salesConversations",
    "quotations",
    "followUpAutomation",
    "crmSynchronization",
    "salesPipeline",
    "orderHandoff",
    "salesAnalytics",
    "salesQaReport",
    "validationReport",
    "validationHistory",
    "completionChecklist",
    "commercePublishingTransition",
    "founderNotification",
    "dashboardUpdate",
    "auditSummary",
    "departmentMetrics",
    "knowledgeBaseEntries",
    "risks",
    "assumptions",
    "nextActions",
    "employeeOutputs",
    "overallScore",
]

REQUIRED_EMPLOYEES = {f"EMP-{number}" for number in range(401, 411)}


def validate_sales_package_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "SALES_PACKAGE":
        issues.append("reportType must be SALES_PACKAGE")
    if data.get("department") != "SALES":
        issues.append("department must be SALES")
    if data.get("departmentStatus") != "COMPLETED":
        issues.append("departmentStatus must be COMPLETED")
    if data.get("marketingPackageLoaded") is not True:
        issues.append("marketingPackageLoaded must be true")
    if data.get("departmentVisibleInWorkflow") is not True:
        issues.append("departmentVisibleInWorkflow must be true")
    if not data.get("communicationChannels"):
        issues.append("communicationChannels is required")
    lead_qualification = data.get("leadQualification", {})
    if not lead_qualification.get("leads"):
        issues.append("leadQualification.leads is required")
    else:
        for lead in lead_qualification["leads"]:
            for key in ["leadId", "source", "score", "priority", "followUpRecommendation"]:
                if key not in lead:
                    issues.append(f"lead missing key: {key}")
    if not data.get("salesConversations", {}).get("conversationPlaybooks"):
        issues.append("salesConversations.conversationPlaybooks is required")
    quotes = data.get("quotations", {}).get("quotes", [])
    if not quotes:
        issues.append("quotations.quotes is required")
    else:
        for quote in quotes:
            for key in ["quoteId", "customerId", "productDetails", "quantity", "unitPrice", "discount", "taxes", "shippingEstimate", "total", "validityPeriod", "terms"]:
                if key not in quote:
                    issues.append(f"quote missing key: {key}")
    if not data.get("followUpAutomation", {}).get("followUpSchedules"):
        issues.append("followUpAutomation.followUpSchedules is required")
    if not data.get("followUpAutomation", {}).get("stopConditions"):
        issues.append("followUpAutomation.stopConditions is required")
    crm = data.get("crmSynchronization", {})
    for key in ["customerRecords", "duplicateDetection", "historyPreserved", "accessControl"]:
        if not crm.get(key):
            issues.append(f"crmSynchronization.{key} is required")
    pipeline = data.get("salesPipeline", {})
    for key in ["stageConfiguration", "opportunities", "transitionAudit", "lostReasons"]:
        if not pipeline.get(key):
            issues.append(f"salesPipeline.{key} is required")
    order_handoff = data.get("orderHandoff", {})
    for key in ["orders", "fulfilmentNotifications", "customerConfirmations"]:
        if not order_handoff.get(key):
            issues.append(f"orderHandoff.{key} is required")
    analytics = data.get("salesAnalytics", {})
    for key in ["metrics", "trends", "reports", "dashboardUpdate"]:
        if not analytics.get(key):
            issues.append(f"salesAnalytics.{key} is required")
    if data.get("commercePublishingTransition", {}).get("status") != "READY":
        issues.append("commercePublishingTransition.status must be READY")
    if data.get("validationReport", {}).get("status") != "PASS":
        issues.append("validationReport.status must be PASS")
    for key in ["completionChecklist", "knowledgeBaseEntries", "risks", "assumptions", "nextActions"]:
        if not data.get(key):
            issues.append(f"{key} is required")
    employee_ids = {output.get("employeeId") for output in data.get("employeeOutputs", []) if isinstance(output, dict)}
    missing = REQUIRED_EMPLOYEES - employee_ids
    if missing:
        issues.append(f"missing employee outputs: {sorted(missing)}")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_sales_package(path: Path) -> list[str]:
    return validate_sales_package_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-sales-package.json")
    issues = validate_sales_package(path)
    if issues:
        print("FAIL: sales package validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis sales package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

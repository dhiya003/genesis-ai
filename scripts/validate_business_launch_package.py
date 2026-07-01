#!/usr/bin/env python3
"""Validate a Genesis Sprint 6 Business Launch Package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "projectId",
    "launchId",
    "marketingId",
    "creativeId",
    "productId",
    "workflowId",
    "department",
    "departmentName",
    "departmentStatus",
    "commerceDepartment",
    "manager",
    "commerceManager",
    "commerceExecutionPlan",
    "executiveSummary",
    "productCatalogue",
    "catalogueSearch",
    "catalogueVersionHistory",
    "productLifecycle",
    "channelsDetected",
    "launchChecklist",
    "marketplacePublishingPlan",
    "socialPublishingPlan",
    "contentSchedule",
    "assetRepository",
    "storeManagementPlan",
    "inventorySynchronization",
    "pricingSynchronization",
    "campaignLaunchPlan",
    "approvalPlan",
    "notificationPlan",
    "publishingPlan",
    "rollbackPlan",
    "launchMonitoring",
    "launchValidation",
    "launchStatus",
    "launchReport",
    "founderNotification",
    "businessIntelligenceTransition",
    "workflowTransition",
    "auditSummary",
    "departmentMetrics",
    "knowledgeBaseEntries",
    "risks",
    "assumptions",
    "nextActions",
    "employeeOutputs",
    "overallScore",
]

REQUIRED_EMPLOYEES = {f"EMP-{number}" for number in range(201, 209)}


def validate_business_launch_package_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "BUSINESS_LAUNCH_PACKAGE":
        issues.append("reportType must be BUSINESS_LAUNCH_PACKAGE")
    if data.get("department") != "COMMERCE_AND_PUBLISHING":
        issues.append("department must be COMMERCE_AND_PUBLISHING")
    if data.get("departmentStatus") != "COMPLETED":
        issues.append("departmentStatus must be COMPLETED")
    if not data.get("commerceManager"):
        issues.append("commerceManager is required")
    catalogue = data.get("productCatalogue", {})
    items = catalogue.get("items", [])
    if not items:
        issues.append("productCatalogue.items is required")
    skus = [item.get("sku") for item in items if isinstance(item, dict)]
    if len(skus) != len(set(skus)):
        issues.append("productCatalogue SKUs must be unique")
    for key in ["searchSupported", "versionHistoryMaintained", "lifecycleTracked", "variantsLinked"]:
        if catalogue.get(key) is not True:
            issues.append(f"productCatalogue.{key} must be true")
    if not data.get("channelsDetected"):
        issues.append("channelsDetected is required")
    if not data.get("launchChecklist"):
        issues.append("launchChecklist is required")
    if not data.get("marketplacePublishingPlan", {}).get("listings"):
        issues.append("marketplacePublishingPlan.listings is required")
    if not data.get("socialPublishingPlan", {}).get("channels"):
        issues.append("socialPublishingPlan.channels is required")
    if not data.get("contentSchedule", {}).get("schedule"):
        issues.append("contentSchedule.schedule is required")
    if not data.get("assetRepository", {}).get("assets"):
        issues.append("assetRepository.assets is required")
    if not data.get("storeManagementPlan", {}).get("catalog"):
        issues.append("storeManagementPlan.catalog is required")
    inventory = data.get("inventorySynchronization", {})
    for key in ["negativeInventoryPrevented", "stockChangesAudited", "syncFailuresReported", "manualReconciliationSupported"]:
        if inventory.get(key) is not True:
            issues.append(f"inventorySynchronization.{key} must be true")
    pricing = data.get("pricingSynchronization", {})
    for key in ["basePriceMaintained", "channelOverridesSupported", "priceHistoryStored", "effectiveDatesSupported", "synchronizationLogged"]:
        if pricing.get(key) is not True:
            issues.append(f"pricingSynchronization.{key} must be true")
    if not data.get("campaignLaunchPlan", {}).get("campaigns"):
        issues.append("campaignLaunchPlan.campaigns is required")
    if not data.get("approvalPlan", {}).get("approvalGates"):
        issues.append("approvalPlan.approvalGates is required")
    if not data.get("notificationPlan", {}).get("notifications"):
        issues.append("notificationPlan.notifications is required")
    if not data.get("publishingPlan", {}).get("executionMode"):
        issues.append("publishingPlan.executionMode is required")
    if not data.get("rollbackPlan", {}).get("supportedActions"):
        issues.append("rollbackPlan.supportedActions is required")
    monitoring = data.get("launchMonitoring", {})
    if monitoring.get("activeDuringLaunch") is not True or not monitoring.get("failureCategories") or not monitoring.get("recoveryRecommendations"):
        issues.append("launchMonitoring must be active with failure categories and recovery recommendations")
    validation = data.get("launchValidation", {})
    if not isinstance(validation.get("score"), (int, float)) or not 0 <= validation.get("score", -1) <= 100:
        issues.append("launchValidation.score must be 0-100")
    if "recommendation" not in validation:
        issues.append("launchValidation.recommendation is required")
    if not data.get("launchReport", {}).get("channelsPrepared"):
        issues.append("launchReport.channelsPrepared is required")
    launch_report = data.get("launchReport", {})
    for key in ["versionControlled", "searchable", "downloadable", "linkedToProject", "warnings", "failures", "recommendations"]:
        if key not in launch_report:
            issues.append(f"launchReport.{key} is required")
    if data.get("workflowTransition") != "BUSINESS_INTELLIGENCE":
        issues.append("workflowTransition must be BUSINESS_INTELLIGENCE")
    if not data.get("businessIntelligenceTransition", {}).get("nextDepartment"):
        issues.append("businessIntelligenceTransition.nextDepartment is required")
    for key in ["auditSummary", "departmentMetrics", "knowledgeBaseEntries"]:
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


def validate_business_launch_package(path: Path) -> list[str]:
    return validate_business_launch_package_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-business-launch-package.json")
    issues = validate_business_launch_package(path)
    if issues:
        print("FAIL: business launch package validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis business launch package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

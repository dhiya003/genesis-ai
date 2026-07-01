#!/usr/bin/env python3
"""Validate a Genesis v3 Enterprise Organization package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED = ["reportType", "organizationId", "organization", "businessPortfolio", "humanWorkforce", "aiWorkforce", "teamCollaboration", "approvalWorkflows", "securityAccessControl", "complianceGovernance", "enterpriseDashboard", "completionStatus", "platformCapabilities", "overallScore"]


def validate_enterprise_organization_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = [f"missing top-level key: {key}" for key in REQUIRED if key not in data]
    if data.get("reportType") != "ENTERPRISE_ORGANIZATION":
        issues.append("reportType must be ENTERPRISE_ORGANIZATION")
    org = data.get("organization", {})
    for key in ["created", "organizationIdGenerated", "multipleBusinessUnitsSupported", "multipleDepartmentsSupported", "multipleWorkspacesSupported", "auditRecorded"]:
        if org.get(key) is not True:
            issues.append(f"organization.{key} must be true")
    portfolio = data.get("businessPortfolio", {})
    for key in ["multipleBusinessesSupported", "sharedServicesConfigurable", "separateFinancialReporting", "crossBusinessAnalytics", "portfolioDashboard"]:
        if portfolio.get(key) is not True:
            issues.append(f"businessPortfolio.{key} must be true")
    for section, keys in {
        "humanWorkforce": ["employeeLifecycleSupported", "organizationalHierarchyMaintained", "skillsSearchable", "capacityTracked", "auditMaintained"],
        "aiWorkforce": ["aiEmployeesRegistered", "performanceTracked", "costMonitored", "skillsCatalogued", "departmentAssignmentMaintained"],
        "teamCollaboration": ["collaborationWorkflowsSupported", "taskOwnershipClear", "escalationPathsDefined", "activityHistoryRetained"],
        "approvalWorkflows": ["multiStepApprovalsSupported", "conditionalApprovalsSupported", "delegationSupported", "approvalSlaTracking"],
        "securityAccessControl": ["granularPermissions", "leastPrivilegeEnforcement", "accessReviews", "securityLogs", "policyEnforcement"],
        "complianceGovernance": ["policiesVersioned", "complianceReportsGenerated", "exceptionsTracked", "auditEvidenceRetained"],
        "enterpriseDashboard": ["portfolioViewAvailable", "drillDownSupported", "realTimeMetricsWhereAvailable", "exportSupported", "customWidgetsSupported"],
    }.items():
        for key in keys:
            if data.get(section, {}).get(key) is not True:
                issues.append(f"{section}.{key} must be true")
    status = data.get("completionStatus", {})
    for key in ["enterprisePlatformOperational", "crossBusinessCoordinationAvailable", "enterpriseGovernanceEnforced", "executiveReportingComplete", "foundationReadyForEnterpriseScaleAutomation"]:
        if status.get(key) is not True:
            issues.append(f"completionStatus.{key} must be true")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_enterprise_organization(path: Path) -> list[str]:
    return validate_enterprise_organization_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0] if argv else sys.argv[1] if len(sys.argv) > 1 else "testing/fixtures/sample-enterprise-organization.json")
    issues = validate_enterprise_organization(path)
    if issues:
        print("FAIL: enterprise organization validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis enterprise organization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

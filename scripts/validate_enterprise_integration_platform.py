#!/usr/bin/env python3
"""Validate a Genesis v3 Enterprise Integration Platform package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED = [
    "reportType",
    "platformId",
    "integrationPlatform",
    "connectorFramework",
    "apiGateway",
    "webhookManagement",
    "eventStreaming",
    "dataSynchronization",
    "aiProviderManagement",
    "secretsManagement",
    "observability",
    "completionStatus",
    "overallScore",
]


def _require_true(data: dict[str, Any], section: str, keys: list[str], issues: list[str]) -> None:
    payload = data.get(section, {})
    for key in keys:
        if payload.get(key) is not True:
            issues.append(f"{section}.{key} must be true")


def validate_enterprise_integration_platform_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = [f"missing top-level key: {key}" for key in REQUIRED if key not in data]
    if data.get("reportType") != "ENTERPRISE_INTEGRATION_PLATFORM":
        issues.append("reportType must be ENTERPRISE_INTEGRATION_PLATFORM")
    _require_true(data, "integrationPlatform", ["initialized", "connectorRegistryLoaded", "apiGatewayInitialized", "authenticationConfigured", "auditEnabled", "healthMonitoringEnabled"], issues)
    _require_true(data, "connectorFramework", ["connectorSdkAvailable", "connectorVersioningSupported", "connectorLifecycleManaged", "connectorHealthMonitored", "failedConnectorsIsolated"], issues)
    _require_true(data, "apiGateway", ["secure", "versionedApis", "apiMetricsCollected", "rateLimitingConfigurable", "apiDocumentationGenerated"], issues)
    _require_true(data, "webhookManagement", ["webhooksConfigurable", "retrySupported", "signatureVerification", "eventHistoryMaintained", "failedDeliveriesMonitored"], issues)
    _require_true(data, "eventStreaming", ["eventBusOperational", "eventReplaySupported", "orderingPreservedWhereRequired", "deadLetterHandlingSupported", "eventSchemaVersioned"], issues)
    _require_true(data, "dataSynchronization", ["incrementalSync", "fullSync", "conflictDetection", "conflictResolutionPolicy", "syncAudit"], issues)
    _require_true(data, "aiProviderManagement", ["multipleProvidersSupported", "modelRoutingConfigurable", "costTracking", "fallbackModels", "providerHealthMonitoring"], issues)
    _require_true(data, "secretsManagement", ["secretsEncrypted", "rotationSupported", "accessAudited", "expirationMonitored", "backupSupported"], issues)
    _require_true(data, "observability", ["realTimeMonitoring", "alerting", "dashboards", "rootCauseAnalysisSupport", "historicalRetention"], issues)
    _require_true(data, "completionStatus", ["integrationPlatformOperational", "enterpriseSystemsIntegrated", "platformHealthVisible", "secureCommunicationEnforced", "apisDocumented", "monitoringOperational", "executiveDashboardUpdated", "genesisReadyForEnterpriseScaleIntegrations"], issues)
    if not data.get("connectorFramework", {}).get("connectorTypes"):
        issues.append("connectorFramework.connectorTypes is required")
    if not data.get("webhookManagement", {}).get("supportedEvents"):
        issues.append("webhookManagement.supportedEvents is required")
    if not data.get("eventStreaming", {}).get("events"):
        issues.append("eventStreaming.events is required")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_enterprise_integration_platform(path: Path) -> list[str]:
    return validate_enterprise_integration_platform_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0] if argv else sys.argv[1] if len(sys.argv) > 1 else "testing/fixtures/sample-enterprise-integration-platform.json")
    issues = validate_enterprise_integration_platform(path)
    if issues:
        print("FAIL: enterprise integration platform validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis enterprise integration platform")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

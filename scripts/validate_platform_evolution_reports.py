#!/usr/bin/env python3
"""Validate Genesis platform evolution packages for EPIC-21 through EPIC-25."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPORTS = {
    "AI_AGENT_PLATFORM": {
        "fixture": "testing/fixtures/sample-ai-agent-platform.json",
        "sections": {
            "agentPlatform": ["initialized", "agentRegistryOperational", "agentHealthMonitoringEnabled", "versionControlEnabled", "auditLoggingEnabled"],
            "customAiEmployee": ["employeeCreated", "departmentAssigned", "toolsConfigured", "versioned", "testModeAvailable"],
            "agentBuilder": ["dragAndDropBuilder", "liveValidation", "previewMode", "versionHistory", "publishWorkflow"],
            "workflowDesigner": ["canvasBasedEditor", "validationBeforePublish", "workflowSimulation", "exportImportSupport", "versionManagement"],
            "departmentBuilder": ["departmentCreated", "managerAssigned", "employeeMappingSupported", "lifecycleInheritedFromPlatform"],
            "agentMarketplace": ["browseMarketplace", "installAgent", "versionCompatibilityChecked", "updatesSupported", "ratingsAndReviewsAvailable"],
            "promptSkillLibrary": ["searchableLibrary", "versionControlled", "reusableAcrossOrganizations", "approvalWorkflowForPublishing"],
            "collaborationNetwork": ["secureInterAgentMessaging", "contextPreservation", "conversationHistory", "permissionEnforcement", "collaborationMetrics"],
            "agentGovernance": ["policyEngineOperational", "violationsDetected", "restrictedActionsBlocked", "auditTrailMaintained", "policySimulationAvailable"],
            "completionStatus": ["organizationsCanCreateCustomAiDepartments", "organizationsCanBuildCustomAiEmployees", "visualWorkflowsExecuteSuccessfully", "governancePoliciesEnforced", "marketplaceExtensionsSupported", "platformExtensibilityValidated", "executiveDashboardUpdated"],
        },
    },
    "DIGITAL_ENTERPRISE": {
        "fixture": "testing/fixtures/sample-digital-enterprise.json",
        "sections": {
            "digitalTwinEngine": ["initialized", "liveSynchronization", "historicalSnapshots", "eventReplay", "healthMonitoring"],
            "liveEnterpriseGraph": ["liveGraph", "relationshipTracking", "impactAnalysis", "dependencyAnalysis", "changeHistory"],
            "enterpriseSimulation": ["fullEnterpriseSimulation", "departmentInteraction", "financialProjection", "resourceProjection"],
            "predictiveBusinessHealth": ["predictionEngine", "earlyWarning", "confidenceScore", "suggestedMitigation"],
            "optimizationEngine": ["optimizationRecommendations", "tradeOffAnalysis", "executiveApprovalWorkflow"],
            "initiativeGeneration": ["initiativeProposal", "roiEstimate", "risks", "requiredApprovals"],
            "portfolioManagement": ["portfolioDashboard", "sharedResources", "crossBusinessOpportunities"],
            "resourceMarketplace": ["resourceMarketplace", "capacityManagement", "allocationEngine"],
            "executiveCopilot": ["executiveCopilots", "sharedContext", "independentReasoning", "collaborativePlanning"],
            "completionStatus": ["digitalTwinOperational", "enterpriseSimulationOperational", "predictiveAnalyticsOperational", "autonomousInitiativesOperational", "portfolioManagementOperational", "executiveCopilotsOperational"],
        },
    },
    "AUTONOMOUS_ENTERPRISE": {
        "fixture": "testing/fixtures/sample-autonomous-enterprise.json",
        "sections": {
            "goalManagement": ["goalMonitoring", "progressTracking", "goalReprioritizationProposals"],
            "projectCreation": ["projectGeneration", "resourceEstimation", "departmentAssignment"],
            "departmentCoordination": ["conflictResolution", "dependencyManagement", "executiveVisibility"],
            "budgetOptimization": ["budgetSimulations", "roiComparison", "approvalWorkflow"],
            "vendorManagement": ["supplierScoring", "riskAlerts", "alternativeRecommendations"],
            "workforcePlanning": ["capacityPlanning", "skillMatching", "aiHumanCollaboration"],
            "customerSuccess": ["churnPrediction", "retentionCampaigns", "customerHealthScores"],
            "innovationLab": ["experimentDesign", "controlledRollout", "outcomeMeasurement", "knowledgeCapture"],
            "strategicAdvisor": ["weeklyStrategyReports", "monthlyBoardReports", "executiveRecommendations", "scenarioUpdates"],
            "completionStatus": ["goalsMonitoredContinuously", "projectsGeneratedAutomatically", "resourcesOptimized", "vendorsManaged", "workforceBalanced", "innovationPipelineActive", "executiveAdvisoryOperational"],
        },
    },
    "PLATFORM_ECOSYSTEM": {
        "fixture": "testing/fixtures/sample-platform-ecosystem.json",
        "sections": {
            "appMarketplace": ["appMarketplace", "installApps", "updateApps", "versionCompatibility", "appPermissions", "revenueSharing"],
            "departmentSdk": ["sdk", "documentation", "testing", "validation", "marketplacePublishing"],
            "aiEmployeeSdk": ["aiEmployeeSdk", "publishing", "securityValidation", "sandboxedExecution"],
            "pluginFramework": ["pluginLifecycle", "pluginSandbox", "pluginApi", "versioning"],
            "developerPortal": ["developerPortal", "documentation", "apiExplorer", "sdkDownloads"],
            "modelMarketplace": ["dynamicRouting", "costComparison", "qualityComparison", "benchmarking"],
            "businessTemplateMarketplace": ["installBusiness", "cloneBusiness", "configure", "launch"],
            "workflowMarketplace": ["workflowLibrary", "import", "versioning", "ratings"],
            "agentMarketplace": ["marketplace", "install", "configure", "update"],
            "completionStatus": ["marketplaceOperational", "sdksOperational", "developersOnboarded", "thirdPartyEcosystemOperational"],
        },
    },
    "COLLECTIVE_ENTERPRISE_INTELLIGENCE": {
        "fixture": "testing/fixtures/sample-collective-enterprise-intelligence.json",
        "sections": {
            "anonymousBusinessLearning": ["privacyPreserving", "optIn", "knowledgeAggregation"],
            "industryBenchmarkEngine": ["benchmarking", "percentileRanking", "industryInsights"],
            "globalOpportunityDetection": ["countryAnalysis", "industryAnalysis", "trendAnalysis"],
            "collectiveDecisionIntelligence": ["decisionGraph", "confidenceImprovement", "similarityMatching"],
            "recommendationNetwork": ["betterRecommendations", "anonymousLearning"],
            "globalSupplierNetwork": ["supplierGraph", "trustScores", "ratings"],
            "globalTalentNetwork": ["skillMatching", "aiHumanMatching"],
            "knowledgeExchange": ["sharing", "accessControl", "licensing"],
            "globalIntelligence": ["industryIntelligence", "countryIntelligence", "regulatoryIntelligence"],
            "completionStatus": ["globalLearningOperational", "benchmarkingOperational", "opportunityEngineOperational", "globalIntelligenceOperational"],
        },
    },
}


def validate_platform_evolution_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    report_type = data.get("reportType")
    spec = REPORTS.get(str(report_type))
    if spec is None:
        return [f"unknown reportType: {report_type}"]
    for key in ["reportType", "platformId", "version", "createdAt", "workflowId", "overallScore"]:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    for section, keys in spec["sections"].items():
        payload = data.get(section, {})
        if not isinstance(payload, dict):
            issues.append(f"{section} must be an object")
            continue
        for key in keys:
            if payload.get(key) is not True:
                issues.append(f"{section}.{key} must be true")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_path(path: Path) -> list[str]:
    return validate_platform_evolution_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    paths = [Path(item) for item in (argv if argv is not None else sys.argv[1:])]
    if not paths:
        paths = [Path(str(spec["fixture"])) for spec in REPORTS.values()]
    failures: list[str] = []
    for path in paths:
        issues = validate_path(path)
        if issues:
            failures.append(str(path))
            print(f"FAIL: {path}")
            for issue in issues:
                print(f"- {issue}")
        else:
            print(f"PASS: {path} is a valid Genesis platform evolution report")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

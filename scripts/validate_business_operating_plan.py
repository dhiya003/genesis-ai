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
    "sprintName",
    "result",
    "projectId",
    "businessId",
    "launchId",
    "workflowId",
    "department",
    "departmentStatus",
    "runtime",
    "founderVision",
    "executiveCouncil",
    "executiveCouncilStatus",
    "departmentPlans",
    "crossDepartmentLoop",
    "crossDepartmentOrchestration",
    "strategicPlan",
    "businessPlan",
    "businessPlanningEngine",
    "digitalTwin",
    "knowledgeGraph",
    "knowledgeGraphService",
    "businessMemory",
    "businessMemoryService",
    "portfolioPlan",
    "resourcePlan",
    "decisionIntelligence",
    "decisionRegister",
    "approvalPolicy",
    "simulationResults",
    "businessHealth",
    "opportunities",
    "opportunityEngine",
    "risks",
    "riskIntelligenceEngine",
    "recommendations",
    "learningEngine",
    "selfImprovementPlan",
    "integrationRegistry",
    "dashboards",
    "executiveDashboard",
    "observabilityPlan",
    "securityPlan",
    "systemAudit",
    "releaseReadiness",
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
    if data.get("department") != "EXECUTIVE_INTELLIGENCE":
        issues.append("department must be EXECUTIVE_INTELLIGENCE")
    if data.get("departmentStatus") != "COMPLETED":
        issues.append("departmentStatus must be COMPLETED")
    if data.get("result") != "Genesis Business Operating System":
        issues.append("result must be Genesis Business Operating System")
    if not data.get("executiveCouncil"):
        issues.append("executiveCouncil is required")
    council = data.get("executiveCouncilStatus", {})
    for key in ["initialized", "departmentHeadsAssigned", "departmentsRegistered", "metricsEnabled", "auditGenerated"]:
        if council.get(key) is not True:
            issues.append(f"executiveCouncilStatus.{key} must be true")
    if not data.get("departmentPlans"):
        issues.append("departmentPlans is required")
    if "Research Again" not in data.get("crossDepartmentLoop", []):
        issues.append("crossDepartmentLoop must include Research Again")
    orchestration = data.get("crossDepartmentOrchestration", {})
    for key in ["dependenciesResolved", "deliverablesHandedOverAutomatically", "failedDepartmentsBlockDownstreamExecution", "handoffsAudited", "workflowContinuityMaintained"]:
        if orchestration.get(key) is not True:
            issues.append(f"crossDepartmentOrchestration.{key} must be true")
    planning = data.get("businessPlanningEngine", {})
    for key in ["plansGenerated", "departmentObjectivesAligned", "dependenciesIdentified", "milestonesDefined"]:
        if planning.get(key) is not True:
            issues.append(f"businessPlanningEngine.{key} must be true")
    if not data.get("decisionRegister"):
        issues.append("decisionRegister is required")
    for decision in data.get("decisionRegister", []):
        if not all(key in decision for key in ["decision", "reason", "evidence", "confidence", "risk", "alternatives", "expectedOutcome", "approvalRequirement"]):
            issues.append("each decision must include reason, evidence, confidence, risk, alternatives, expectedOutcome, and approvalRequirement")
            break
    decision_intelligence = data.get("decisionIntelligence", {})
    for key in ["everyRecommendationJustified", "confidenceDisplayed", "alternativesIncluded", "risksDocumented", "evidenceLinked"]:
        if decision_intelligence.get(key) is not True:
            issues.append(f"decisionIntelligence.{key} must be true")
    twin = data.get("digitalTwin", {})
    for key in ["products", "inventory", "customers", "marketing", "sales", "operations", "finance", "goals", "kpis", "currentState"]:
        if key not in twin:
            issues.append(f"digitalTwin.{key} is required")
    graph = data.get("knowledgeGraph", {})
    if not graph.get("nodes") or not graph.get("edges"):
        issues.append("knowledgeGraph nodes and edges are required")
    for key in ["impactAnalysisPossible", "crossEntityNavigationSupported", "knowledgeReusable"]:
        if graph.get(key) is not True:
            issues.append(f"knowledgeGraph.{key} must be true")
    for service_name in ["knowledgeGraphService", "businessMemoryService"]:
        service = data.get(service_name, {})
        if service.get("operational") is not True:
            issues.append(f"{service_name}.operational must be true")
    memory = data.get("businessMemory", {})
    for key in ["businesses", "projects", "researchReports", "productBlueprints", "brandAssets", "marketingPlans", "salesReports", "businessReports", "approvals", "decisions"]:
        if key not in memory:
            issues.append(f"businessMemory.{key} is required")
    health = data.get("businessHealth", {})
    if not isinstance(health.get("overallBusinessHealthScore"), (int, float)) or not 0 <= health.get("overallBusinessHealthScore", -1) <= 100:
        issues.append("businessHealth.overallBusinessHealthScore must be 0-100")
    if not data.get("simulationResults"):
        issues.append("simulationResults is required")
    if not data.get("recommendations"):
        issues.append("recommendations is required")
    for recommendation in data.get("recommendations", []):
        if not all(key in recommendation for key in ["evidence", "confidence", "alternatives", "risk", "expectedOutcome"]):
            issues.append("each recommendation must include evidence, confidence, alternatives, risk, and expectedOutcome")
            break
    if not data.get("opportunityEngine", {}).get("opportunities"):
        issues.append("opportunityEngine.opportunities is required")
    risk_engine = data.get("riskIntelligenceEngine", {})
    for key in ["risksDetected", "severityAssigned", "likelihoodEstimated", "mitigationRecommendationsGenerated", "alertsCreated"]:
        if risk_engine.get(key) is not True:
            issues.append(f"riskIntelligenceEngine.{key} must be true")
    if not data.get("approvalPolicy", {}).get("manual"):
        issues.append("approvalPolicy.manual is required")
    dashboard = data.get("executiveDashboard", {})
    for key in ["businessHealth", "revenue", "projects", "departmentStatus", "approvals", "risks", "opportunities", "recommendations", "kpis", "recentActivity"]:
        if key not in dashboard:
            issues.append(f"executiveDashboard.{key} is required")
    for key in ["liveStatusShown", "departmentSummariesAvailable", "drillDownSupported", "mobileFriendly", "exportSupported"]:
        if dashboard.get(key) is not True:
            issues.append(f"executiveDashboard.{key} must be true")
    if data.get("systemAudit", {}).get("completed") is not True:
        issues.append("systemAudit.completed must be true")
    if data.get("releaseReadiness", {}).get("genesisV1ProductionReady") is not True:
        issues.append("releaseReadiness.genesisV1ProductionReady must be true")
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

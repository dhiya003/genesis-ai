#!/usr/bin/env python3
"""Validate a Genesis v2 Simulation Scenario Report."""

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
    "simulationEngine",
    "pricingSimulation",
    "marketingInvestmentSimulation",
    "productLaunchSimulation",
    "supplierChangeSimulation",
    "expansionSimulation",
    "scenarioComparison",
    "executiveRecommendation",
    "simulationLearning",
    "decisionRegisterEntry",
    "completionChecklist",
    "reportGovernance",
    "overallScore",
]


def validate_simulation_report_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "SIMULATION_SCENARIO_REPORT":
        issues.append("reportType must be SIMULATION_SCENARIO_REPORT")
    engine = data.get("simulationEngine", {})
    for key in ["initialized", "businessContextLoaded", "businessMemoryConnected", "knowledgeGraphConnected", "executiveDashboardUpdated", "auditCreated"]:
        if engine.get(key) is not True:
            issues.append(f"simulationEngine.{key} must be true")
    pricing = data.get("pricingSimulation", {})
    for key in ["multipleScenariosSupported", "sideBySideComparison", "risksExplained", "confidenceDisplayed", "historicalComparisonAvailable"]:
        if not pricing.get(key):
            issues.append(f"pricingSimulation.{key} is required")
    marketing = data.get("marketingInvestmentSimulation", {})
    for key in ["budgetScenariosSupported", "channelsCompared", "risksExplained", "assumptionsDocumented", "confidenceCalculated"]:
        if not marketing.get(key):
            issues.append(f"marketingInvestmentSimulation.{key} is required")
    product = data.get("productLaunchSimulation", {})
    for key in ["launchFeasibilityEstimated", "operationalRisksIdentified", "financialImpactEstimated", "resourceRequirementsDisplayed", "executiveRecommendationGenerated"]:
        if not product.get(key):
            issues.append(f"productLaunchSimulation.{key} is required")
    supplier = data.get("supplierChangeSimulation", {})
    for key in ["supplierComparisonGenerated", "costDifferenceCalculated", "risksIdentified", "alternativesRanked", "recommendationProvided"]:
        if not supplier.get(key):
            issues.append(f"supplierChangeSimulation.{key} is required")
    expansion = data.get("expansionSimulation", {})
    for key in ["expansionOpportunitiesAnalyzed", "estimatedInvestmentCalculated", "risksAssessed", "expectedBusinessImpactEstimated", "recommendedSequenceProvided"]:
        if not expansion.get(key):
            issues.append(f"expansionSimulation.{key} is required")
    comparison = data.get("scenarioComparison", {})
    for key in ["multipleScenariosCompared", "rankingGenerated", "risksCompared", "confidenceDisplayed"]:
        if comparison.get(key) is not True:
            issues.append(f"scenarioComparison.{key} must be true")
    if not comparison.get("kpisCompared"):
        issues.append("scenarioComparison.kpisCompared is required")
    rec = data.get("executiveRecommendation", {})
    for key in ["bestScenarioSelected", "preferredScenario", "justification", "supportingEvidence", "risks", "confidenceScore", "alternativeOptions", "whyOtherOptionsWereRejected", "evidenceLinked"]:
        if key not in rec or not rec.get(key):
            issues.append(f"executiveRecommendation.{key} is required")
    learning = data.get("simulationLearning", {})
    for key in ["predictionsTracked", "actualOutcomesCaptured", "accuracyMeasured", "learningHistoryUpdated", "modelsImprovedUsingOrganizationalKnowledge"]:
        if learning.get(key) is not True:
            issues.append(f"simulationLearning.{key} must be true")
    governance = data.get("reportGovernance", {})
    for key in ["searchable", "versioned", "linkedToBusiness", "linkedToProject", "historicalComparisonsAvailable", "recommendationsReusable", "executiveNotified"]:
        if governance.get(key) is not True:
            issues.append(f"reportGovernance.{key} must be true")
    if not data.get("decisionRegisterEntry"):
        issues.append("decisionRegisterEntry is required")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_simulation_report(path: Path) -> list[str]:
    return validate_simulation_report_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0] if argv else sys.argv[1] if len(sys.argv) > 1 else "testing/fixtures/sample-simulation-report.json")
    issues = validate_simulation_report(path)
    if issues:
        print("FAIL: simulation report validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis simulation report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

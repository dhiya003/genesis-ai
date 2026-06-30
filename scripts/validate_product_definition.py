#!/usr/bin/env python3
"""Validate a Genesis Sprint 3 Product Definition using strict stdlib checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "projectId",
    "workflowId",
    "sourceReportId",
    "sourceWorkflowId",
    "sourceIdea",
    "department",
    "manager",
    "productDefinitionDocument",
    "opportunityReport",
    "variantMatrix",
    "productRoadmap",
    "constraintsReport",
    "successMetrics",
    "riskRegister",
    "approvalChecklist",
    "knowledgeBaseEntries",
]

REQUIRED_PRODUCT_DEFINITION_FIELDS = [
    "projectId",
    "sourceReportId",
    "productName",
    "category",
    "purpose",
    "problemSolved",
    "targetCustomer",
    "ageGroup",
    "useCase",
    "productStory",
    "differentiator",
    "variants",
    "futureRoadmap",
    "evidence",
    "assumptions",
]

REQUIRED_OPPORTUNITY_SCORES = [
    "customerValue",
    "marketGap",
    "competition",
    "manufacturingDifficulty",
    "profit",
    "differentiation",
    "scalability",
    "supplierAvailability",
    "inventoryRisk",
    "shippingRisk",
    "learningValue",
]

REQUIRED_VARIANTS = {"Starter", "Standard", "Premium", "Bundle", "Subscription", "Accessories", "Expansion Packs"}

REQUIRED_SUCCESS_METRICS = [
    "complexityScore",
    "manufacturabilityScore",
    "innovationScore",
    "profitabilityScore",
    "customerValueScore",
    "shippingScore",
    "packagingScore",
    "expansionPotential",
    "overallProductScore",
]


def validate_product_definition_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "PRODUCT_DEFINITION":
        issues.append("reportType must be PRODUCT_DEFINITION")
    if data.get("department") != "PRODUCT":
        issues.append("department must be PRODUCT")
    product_definition = data.get("productDefinitionDocument")
    if not isinstance(product_definition, dict):
        issues.append("productDefinitionDocument must be an object")
    else:
        for key in REQUIRED_PRODUCT_DEFINITION_FIELDS:
            if key not in product_definition:
                issues.append(f"missing productDefinitionDocument key: {key}")
        if not isinstance(product_definition.get("variants"), list) or not product_definition.get("variants"):
            issues.append("productDefinitionDocument.variants must be a non-empty list")
        if not isinstance(product_definition.get("assumptions"), list) or not product_definition.get("assumptions"):
            issues.append("productDefinitionDocument.assumptions must be a non-empty list")
    opportunity_report = data.get("opportunityReport")
    if not isinstance(opportunity_report, dict):
        issues.append("opportunityReport must be an object")
    else:
        scores = opportunity_report.get("scores")
        if not isinstance(scores, dict):
            issues.append("opportunityReport.scores must be an object")
        else:
            for key in REQUIRED_OPPORTUNITY_SCORES:
                _check_score(scores.get(key), f"opportunityReport.scores.{key}", issues)
        _check_score(opportunity_report.get("overallOpportunityScore"), "opportunityReport.overallOpportunityScore", issues)
        if not isinstance(opportunity_report.get("rejectedAlternatives"), list) or not opportunity_report.get("rejectedAlternatives"):
            issues.append("opportunityReport.rejectedAlternatives must be a non-empty list")
    variant_matrix = data.get("variantMatrix")
    if not isinstance(variant_matrix, list):
        issues.append("variantMatrix must be a list")
    else:
        levels = {item.get("level") for item in variant_matrix if isinstance(item, dict)}
        missing = sorted(REQUIRED_VARIANTS - levels)
        if missing:
            issues.append(f"variantMatrix missing levels: {missing}")
    for key in ["productRoadmap", "constraintsReport"]:
        if not isinstance(data.get(key), dict) or not data.get(key):
            issues.append(f"{key} must be a non-empty object")
    success_metrics = data.get("successMetrics")
    if not isinstance(success_metrics, dict):
        issues.append("successMetrics must be an object")
    else:
        for key in REQUIRED_SUCCESS_METRICS:
            _check_score(success_metrics.get(key), f"successMetrics.{key}", issues)
    for key in ["riskRegister", "approvalChecklist", "knowledgeBaseEntries"]:
        if not isinstance(data.get(key), list) or not data.get(key):
            issues.append(f"{key} must be a non-empty list")
    return issues


def validate_product_definition(path: Path) -> list[str]:
    return validate_product_definition_payload(json.loads(path.read_text(encoding="utf-8")))


def _check_score(value: Any, label: str, issues: list[str]) -> None:
    if not isinstance(value, (int, float)) or not 0 <= value <= 100:
        issues.append(f"{label} must be a number from 0 to 100")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-product-definition.json")
    issues = validate_product_definition(path)
    if issues:
        print("FAIL: product definition validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis product definition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

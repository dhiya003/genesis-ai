#!/usr/bin/env python3
"""Validate a Genesis Sprint 3 Product Blueprint using stdlib checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "projectId",
    "productId",
    "workflowId",
    "sourceReportId",
    "sourceWorkflowId",
    "sourceIdea",
    "department",
    "departmentStatus",
    "productName",
    "executiveSummary",
    "departmentInitialization",
    "productManager",
    "productExecutionPlan",
    "productStrategy",
    "productSpecification",
    "productDefinition",
    "productFeatures",
    "productVariants",
    "productRoadmap",
    "customerFit",
    "productConstraints",
    "productSuccessMetrics",
    "productArchitecture",
    "productConceptValidation",
    "engineeringSpecification",
    "materialRecommendation",
    "materialRecommendations",
    "manufacturabilityEvaluation",
    "manufacturingPlan",
    "manufacturingMethodSelection",
    "bom",
    "costAnalysis",
    "pricingStrategy",
    "packagingSpecification",
    "shippingPlan",
    "shippingAssessment",
    "supplierRecommendations",
    "qualityChecklist",
    "qualityAssessment",
    "profitabilityReport",
    "profitabilityAnalysis",
    "blueprintValidationReport",
    "validationHistory",
    "risks",
    "assumptions",
    "recommendations",
    "nextActions",
    "launchReadyEngineeringPackage",
    "productReviewGate",
    "completionChecklist",
    "creativeStudioTransition",
    "founderNotification",
    "departmentMetrics",
    "auditSummary",
    "employeeOutputs",
    "overallScore",
]

REQUIRED_EMPLOYEES = {f"EMP-{number}" for number in range(101, 111)}
REQUIRED_VARIANTS = {"Starter", "Standard", "Premium"}
REQUIRED_BLUEPRINT_SECTIONS = {
    "engineeringSpecification": ["dimensions", "materials", "assemblyMethod", "manufacturingProcess", "manufacturingDifficulty", "toolingRequirements", "safetyConsiderations", "estimatedProductionTime"],
    "materialRecommendation": ["primaryMaterials", "alternativeMaterials", "materialComparison", "costComparison", "durabilityComparison", "availabilityAssessment"],
    "manufacturingPlan": ["manufacturingTechnology", "manufacturingSequence", "processFlow", "productionAssumptions", "expectedYield", "manufacturingRisks"],
    "bom": ["version", "linkedProductBlueprint", "items", "totalEstimatedCost"],
    "costAnalysis": ["rawMaterialCost", "manufacturingCost", "assemblyCost", "packagingCost", "labelCost", "shippingCost", "warehousingCost", "marketingAllowance", "marketplaceFees", "taxes", "returnsAllowance", "miscBuffer", "landedCost", "grossMargin", "netMargin", "breakEvenQuantity", "roiEstimate", "costAssumptions", "sensitivityAnalysis"],
    "pricingStrategy": ["manufacturingPrice", "wholesalePrice", "distributorPrice", "retailPrice", "marketplaceSellingPrice", "premiumPricingOption", "bundlePricing"],
    "packagingSpecification": ["packagingDimensions", "primaryPackaging", "secondaryPackaging", "protectiveInserts", "packagingMaterials", "labels", "barcodes", "qrCodes", "protectionStrategy", "shippingOptimization", "storageOptimization", "storageRequirements", "brandingRequirements", "estimatedPackagingCost", "sustainabilityAssessment"],
    "supplierRecommendations": ["shortlist", "comparison", "alternativeSuppliers"],
    "profitabilityReport": ["profitPerUnit", "profitPercentage", "suggestedSellingPrice", "wholesalePrice", "marketplacePrice", "grossMargin", "netMarginEstimated", "breakEvenQuantity", "roi", "profitabilityRating", "assumptions", "marginScore", "scalabilityScore", "inventoryRisk", "cashFlowImpact"],
}


def validate_product_blueprint_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "PRODUCT_BLUEPRINT":
        issues.append("reportType must be PRODUCT_BLUEPRINT")
    if data.get("department") != "PRODUCT":
        issues.append("department must be PRODUCT")
    _check_score(data.get("overallScore"), "overallScore", issues)
    variants = data.get("productVariants")
    if not isinstance(variants, list) or not variants:
        issues.append("productVariants must be a non-empty list")
    else:
        levels = {item.get("level") for item in variants if isinstance(item, dict)}
        missing = sorted(REQUIRED_VARIANTS - levels)
        if missing:
            issues.append(f"productVariants missing levels: {missing}")
    for section, keys in REQUIRED_BLUEPRINT_SECTIONS.items():
        value = data.get(section)
        if not isinstance(value, dict):
            issues.append(f"{section} must be an object")
            continue
        for key in keys:
            if key not in value:
                issues.append(f"{section} missing key: {key}")
    bom_items = data.get("bom", {}).get("items") if isinstance(data.get("bom"), dict) else None
    if not isinstance(bom_items, list) or not bom_items:
        issues.append("bom.items must be a non-empty list")
    else:
        for index, item in enumerate(bom_items):
            if not isinstance(item, dict):
                issues.append(f"bom.items[{index}] must be an object")
                continue
            for key in ["partNumber", "component", "quantity", "material", "estimatedUnitCost", "supplierCategory", "componentId", "componentName", "category", "unitOfMeasure", "unitCostEstimated", "criticality", "optionalAlternatives", "notes"]:
                if key not in item:
                    issues.append(f"bom.items[{index}] missing key: {key}")
    supplier_shortlist = data.get("supplierRecommendations", {}).get("shortlist") if isinstance(data.get("supplierRecommendations"), dict) else None
    if not isinstance(supplier_shortlist, list) or not supplier_shortlist:
        issues.append("supplierRecommendations.shortlist must be a non-empty list")
    else:
        for index, supplier in enumerate(supplier_shortlist):
            if not isinstance(supplier, dict):
                issues.append(f"supplierRecommendations.shortlist[{index}] must be an object")
                continue
            for key in ["name", "country", "location", "productRange", "estimatedPricing", "qualityIndicators", "capacity", "moq", "leadTimeDays", "riskScore", "risks", "linkedBomItems"]:
                if key not in supplier:
                    issues.append(f"supplierRecommendations.shortlist[{index}] missing key: {key}")
    shipping = data.get("shippingAssessment")
    if not isinstance(shipping, dict) or not all(key in shipping for key in ["estimatedWeightGrams", "estimatedDimensions", "courierSuitability", "exportReadiness", "fragilityAssessment", "risks", "recommendations"]):
        issues.append("shippingAssessment must include readiness, dimensions, risks, and recommendations")
    quality = data.get("qualityAssessment")
    if not isinstance(quality, dict) or not all(key in quality for key in ["failureModes", "assemblyRisks", "materialRisks", "durabilityRisks", "safetyRisks", "customerExperienceRisks", "inspectionRecommendations"]):
        issues.append("qualityAssessment must include risk categories and inspection recommendations")
    for key in ["qualityChecklist", "risks", "assumptions", "recommendations", "nextActions"]:
        if not isinstance(data.get(key), list) or not data.get(key):
            issues.append(f"{key} must be a non-empty list")
    package = data.get("launchReadyEngineeringPackage")
    if not isinstance(package, dict) or package.get("readyForSupplierDiscussion") is not True:
        issues.append("launchReadyEngineeringPackage.readyForSupplierDiscussion must be true")
    review_gate = data.get("productReviewGate")
    if not isinstance(review_gate, dict) or review_gate.get("approvedForCreativeStudio") is not True:
        issues.append("productReviewGate.approvedForCreativeStudio must be true")
    if data.get("creativeStudioTransition", {}).get("status") != "READY":
        issues.append("creativeStudioTransition.status must be READY")
    if data.get("departmentStatus") != "COMPLETED":
        issues.append("departmentStatus must be COMPLETED")
    for key in ["blueprintValidationReport", "validationHistory", "completionChecklist", "departmentMetrics"]:
        if not data.get(key):
            issues.append(f"{key} is required")
    employee_outputs = data.get("employeeOutputs")
    if not isinstance(employee_outputs, list):
        issues.append("employeeOutputs must be a list")
    else:
        employee_ids = {item.get("employeeId") for item in employee_outputs if isinstance(item, dict)}
        missing = sorted(REQUIRED_EMPLOYEES - employee_ids)
        if missing:
            issues.append(f"employeeOutputs missing employees: {missing}")
        for output in employee_outputs:
            if not isinstance(output, dict):
                continue
            validation = output.get("validation")
            if not isinstance(validation, dict) or not all(validation.get(key) == "PASS" for key in ["schema", "business", "engineering", "confidence", "risk"]):
                issues.append(f"{output.get('employeeId')} validation gates must all PASS")
    return issues


def validate_product_blueprint(path: Path) -> list[str]:
    return validate_product_blueprint_payload(json.loads(path.read_text(encoding="utf-8")))


def _check_score(value: Any, label: str, issues: list[str]) -> None:
    if not isinstance(value, (int, float)) or not 0 <= value <= 100:
        issues.append(f"{label} must be a number from 0 to 100")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-product-blueprint.json")
    issues = validate_product_blueprint(path)
    if issues:
        print("FAIL: product blueprint validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis product blueprint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

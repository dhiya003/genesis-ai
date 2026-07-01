#!/usr/bin/env python3
"""Validate a Genesis Sprint 4 Creative Pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "projectId",
    "creativeId",
    "productId",
    "workflowId",
    "department",
    "departmentStatus",
    "creativeStudio",
    "creativeDirector",
    "creativeExecutionPlan",
    "brandContext",
    "workflowUpdate",
    "productBlueprintApproval",
    "brandStrategy",
    "brandStrategyDocument",
    "brandNameRecommendation",
    "brandIdentity",
    "brandGuidelinesDocument",
    "logoSystem",
    "logoVariants",
    "logoUsageRules",
    "colorPalette",
    "typography",
    "visualIdentityRules",
    "visualSystem",
    "packagingDesignBrief",
    "packagingProductionAssets",
    "productMockupBrief",
    "productCreativeDeliverables",
    "marketplaceCreativePack",
    "socialMediaCreativePack",
    "digitalAssets",
    "launchCopyPack",
    "aiDeliverables",
    "creativeAssetManifest",
    "generatedAssets",
    "productionReadiness",
    "creativeQaReport",
    "validationReport",
    "creativeValidationReport",
    "validationHistory",
    "founderApprovalChecklist",
    "risks",
    "assumptions",
    "nextActions",
    "assetGenerationPrompts",
    "marketingTransition",
    "founderNotification",
    "departmentMetrics",
    "auditSummary",
    "knowledgeBaseEntries",
    "employeeOutputs",
    "overallScore",
]

REQUIRED_EMPLOYEES = {f"EMP-{number}" for number in range(201, 211)}


def validate_creative_pack_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "CREATIVE_PACK":
        issues.append("reportType must be CREATIVE_PACK")
    if data.get("department") != "CREATIVE":
        issues.append("department must be CREATIVE")
    if data.get("departmentStatus") != "COMPLETED":
        issues.append("departmentStatus must be COMPLETED")
    for key in ["creativeStudio", "creativeDirector", "creativeExecutionPlan", "brandContext", "workflowUpdate", "productBlueprintApproval"]:
        if not isinstance(data.get(key), dict) or not data.get(key):
            issues.append(f"{key} must be a non-empty object")
    if data.get("productBlueprintApproval", {}).get("approvedForCreativeStudio") is not True:
        issues.append("productBlueprintApproval.approvedForCreativeStudio must be true")
    if not data.get("brandIdentity", {}).get("brandName"):
        issues.append("brandIdentity.brandName is required")
    for key in ["brandStory", "mission", "vision", "brandGuidelines"]:
        if not data.get("brandIdentity", {}).get(key):
            issues.append(f"brandIdentity.{key} is required")
    if not data.get("logoVariants"):
        issues.append("logoVariants is required")
    strategy = data.get("brandStrategy", {})
    for key in ["brandPurpose", "brandMission", "brandVision", "valueProposition", "emotionalPositioning", "competitivePositioning", "brandArchetype", "positioning", "targetAudience"]:
        if key not in strategy:
            issues.append(f"brandStrategy missing key: {key}")
    guidelines = data.get("brandGuidelinesDocument", {})
    for key in ["logo", "colors", "typography", "spacing", "imagery", "illustration", "iconography", "tone", "copy", "accessibility", "do", "dont"]:
        if key not in guidelines:
            issues.append(f"brandGuidelinesDocument missing key: {key}")
    if not data.get("visualSystem", {}).get("designTokens"):
        issues.append("visualSystem.designTokens is required")
    if len(data.get("colorPalette", [])) < 3:
        issues.append("colorPalette must contain at least 3 colors")
    if not data.get("packagingDesignBrief", {}).get("panelContent"):
        issues.append("packagingDesignBrief.panelContent is required")
    if not data.get("packagingProductionAssets", {}).get("printReadyDielines"):
        issues.append("packagingProductionAssets.printReadyDielines is required")
    if not data.get("productMockupBrief", {}).get("variantMockups"):
        issues.append("productMockupBrief.variantMockups is required")
    product_creatives = data.get("productCreativeDeliverables", {})
    for key in ["heroImages", "lifestyleImages", "explodedViews", "productManuals", "instructionCards"]:
        if not product_creatives.get(key):
            issues.append(f"productCreativeDeliverables.{key} is required")
    if not data.get("marketplaceCreativePack", {}).get("imageConcepts"):
        issues.append("marketplaceCreativePack.imageConcepts is required")
    if not data.get("socialMediaCreativePack", {}).get("instagramPosts"):
        issues.append("socialMediaCreativePack.instagramPosts is required")
    if not data.get("digitalAssets", {}).get("amazonImageSet"):
        issues.append("digitalAssets.amazonImageSet is required")
    if not data.get("aiDeliverables", {}).get("masterImagePrompts"):
        issues.append("aiDeliverables.masterImagePrompts is required")
    if not data.get("creativeAssetManifest"):
        issues.append("creativeAssetManifest is required")
    generated_assets = data.get("generatedAssets", {})
    if not generated_assets.get("assets"):
        issues.append("generatedAssets.assets is required")
    generated_summary = generated_assets.get("summary", {})
    for key in ["svg", "png", "pdf"]:
        if not isinstance(generated_summary.get(key), int) or generated_summary.get(key, 0) < 1:
            issues.append(f"generatedAssets.summary.{key} must be at least 1")
    if not data.get("validationReport"):
        issues.append("validationReport is required")
    creative_validation = data.get("creativeValidationReport")
    if not isinstance(creative_validation, dict) or creative_validation.get("status") != "PASS":
        issues.append("creativeValidationReport.status must be PASS")
    else:
        for key in ["validationAreas", "errors", "warnings", "failedAssetsBlocked", "validationHistory"]:
            if key not in creative_validation:
                issues.append(f"creativeValidationReport missing key: {key}")
    if not data.get("launchCopyPack", {}).get("taglines"):
        issues.append("launchCopyPack.taglines is required")
    if not data.get("founderApprovalChecklist"):
        issues.append("founderApprovalChecklist is required")
    if data.get("marketingTransition", {}).get("status") != "READY":
        issues.append("marketingTransition.status must be READY")
    for key in ["validationHistory", "departmentMetrics", "auditSummary", "knowledgeBaseEntries"]:
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


def validate_creative_pack(path: Path) -> list[str]:
    return validate_creative_pack_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-creative-pack.json")
    issues = validate_creative_pack(path)
    if issues:
        print("FAIL: creative pack validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis creative pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

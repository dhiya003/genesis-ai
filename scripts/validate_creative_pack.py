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
    "brandStrategy",
    "brandNameRecommendation",
    "brandIdentity",
    "logoSystem",
    "colorPalette",
    "typography",
    "visualIdentityRules",
    "packagingDesignBrief",
    "productMockupBrief",
    "marketplaceCreativePack",
    "socialMediaCreativePack",
    "launchCopyPack",
    "creativeQaReport",
    "founderApprovalChecklist",
    "risks",
    "assumptions",
    "nextActions",
    "assetGenerationPrompts",
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
    if not data.get("brandIdentity", {}).get("brandName"):
        issues.append("brandIdentity.brandName is required")
    if len(data.get("colorPalette", [])) < 3:
        issues.append("colorPalette must contain at least 3 colors")
    if not data.get("packagingDesignBrief", {}).get("panelContent"):
        issues.append("packagingDesignBrief.panelContent is required")
    if not data.get("productMockupBrief", {}).get("variantMockups"):
        issues.append("productMockupBrief.variantMockups is required")
    if not data.get("marketplaceCreativePack", {}).get("imageConcepts"):
        issues.append("marketplaceCreativePack.imageConcepts is required")
    if not data.get("socialMediaCreativePack", {}).get("instagramPosts"):
        issues.append("socialMediaCreativePack.instagramPosts is required")
    if not data.get("launchCopyPack", {}).get("taglines"):
        issues.append("launchCopyPack.taglines is required")
    if not data.get("founderApprovalChecklist"):
        issues.append("founderApprovalChecklist is required")
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


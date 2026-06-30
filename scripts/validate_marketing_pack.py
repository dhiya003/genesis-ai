#!/usr/bin/env python3
"""Validate a Genesis Sprint 5 Marketing Pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = [
    "reportType",
    "version",
    "projectId",
    "marketingId",
    "creativeId",
    "productId",
    "workflowId",
    "department",
    "marketingStrategy",
    "launchPositioning",
    "customerPersonas",
    "seoPlan",
    "socialMediaPlan",
    "advertisingPlan",
    "marketplaceListing",
    "landingPageCopy",
    "emailCampaign",
    "whatsappCampaign",
    "influencerStrategy",
    "hashtagPlan",
    "launchPlan",
    "campaignQaReport",
    "founderApprovalChecklist",
    "risks",
    "assumptions",
    "nextActions",
    "employeeOutputs",
    "overallScore",
]

REQUIRED_EMPLOYEES = {f"EMP-{number}" for number in range(301, 311)}


def validate_marketing_pack_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "MARKETING_PACK":
        issues.append("reportType must be MARKETING_PACK")
    if data.get("department") != "MARKETING":
        issues.append("department must be MARKETING")
    if not data.get("seoPlan", {}).get("keywords"):
        issues.append("seoPlan.keywords is required")
    if not data.get("socialMediaPlan", {}).get("instagramCalendar"):
        issues.append("socialMediaPlan.instagramCalendar is required")
    if not data.get("advertisingPlan", {}).get("metaAds"):
        issues.append("advertisingPlan.metaAds is required")
    if not data.get("marketplaceListing", {}).get("title"):
        issues.append("marketplaceListing.title is required")
    if not data.get("landingPageCopy", {}).get("hero"):
        issues.append("landingPageCopy.hero is required")
    if not data.get("emailCampaign", {}).get("sequence"):
        issues.append("emailCampaign.sequence is required")
    if not data.get("whatsappCampaign", {}).get("broadcasts"):
        issues.append("whatsappCampaign.broadcasts is required")
    if not data.get("influencerStrategy", {}).get("creatorProfiles"):
        issues.append("influencerStrategy.creatorProfiles is required")
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


def validate_marketing_pack(path: Path) -> list[str]:
    return validate_marketing_pack_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-marketing-pack.json")
    issues = validate_marketing_pack(path)
    if issues:
        print("FAIL: marketing pack validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis marketing pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


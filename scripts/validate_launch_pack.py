#!/usr/bin/env python3
"""Validate a Genesis launch pack fixture using standard-library checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = [
    "reportType",
    "projectId",
    "version",
    "createdAt",
    "founderRequirement",
    "projectTitle",
    "phase1Manual",
    "sections",
    "risks",
    "nextActions",
]

REQUIRED_SECTIONS = ["research", "product", "creative", "marketing", "publishing", "validation"]


def validate_launch_pack(path: Path) -> list[str]:
    issues: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "LAUNCH_PACK":
        issues.append("reportType must be LAUNCH_PACK")
    sections = data.get("sections", {})
    if not isinstance(sections, dict):
        issues.append("sections must be an object")
    else:
        for section in REQUIRED_SECTIONS:
            if section not in sections:
                issues.append(f"missing section: {section}")
    if not data.get("risks"):
        issues.append("risks must not be empty")
    if not data.get("nextActions"):
        issues.append("nextActions must not be empty")
    return issues


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    path = Path(args[0]) if args else Path("testing/fixtures/sample-launch-pack.json")
    issues = validate_launch_pack(path)
    if issues:
        print("FAIL: launch pack validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis launch pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

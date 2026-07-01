#!/usr/bin/env python3
"""Validate a Genesis v2 Organizational Intelligence Report."""

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
    "organizationalMemory",
    "decisionHistory",
    "lessonsLearned",
    "knowledgeGraph",
    "outcomeLearning",
    "businessPatterns",
    "executiveKnowledgeBase",
    "knowledgeReuse",
    "intelligenceReport",
    "completionChecklist",
    "departmentAvailability",
    "auditSummary",
    "overallScore",
]


def validate_organizational_intelligence_report_payload(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            issues.append(f"missing top-level key: {key}")
    if data.get("reportType") != "ORGANIZATIONAL_INTELLIGENCE_REPORT":
        issues.append("reportType must be ORGANIZATIONAL_INTELLIGENCE_REPORT")
    memory = data.get("organizationalMemory", {})
    for key in ["initialized", "knowledgePersisted", "searchSupported", "versionHistoryMaintained", "historicalRetrievalSupported", "auditRecorded"]:
        if memory.get(key) is not True:
            issues.append(f"organizationalMemory.{key} must be true")
    if not data.get("decisionHistory"):
        issues.append("decisionHistory is required")
    for decision in data.get("decisionHistory", []):
        if not all(key in decision for key in ["reason", "evidence", "confidence", "outcomeTracked"]):
            issues.append("each decision must include reason, evidence, confidence, and outcomeTracked")
            break
    if not data.get("lessonsLearned"):
        issues.append("lessonsLearned is required")
    for lesson in data.get("lessonsLearned", []):
        if not lesson.get("category") or lesson.get("searchSupported") is not True or lesson.get("reusableAcrossBusinesses") is not True or not lesson.get("linkedProjectId"):
            issues.append("each lesson must be categorized, searchable, reusable, and linked to project")
            break
    graph = data.get("knowledgeGraph", {})
    for key in ["relationshipsStored", "graphSearchable", "dependenciesNavigable", "impactAnalysisSupported"]:
        if graph.get(key) is not True:
            issues.append(f"knowledgeGraph.{key} must be true")
    learning = data.get("outcomeLearning", {})
    for key in ["predictionsComparedWithOutcomes", "learningHistoryStored", "futureRecommendationsReferencePriorOutcomes"]:
        if learning.get(key) is not True:
            issues.append(f"outcomeLearning.{key} must be true")
    if not learning.get("accuracyMeasured"):
        issues.append("outcomeLearning.accuracyMeasured is required")
    for pattern in data.get("businessPatterns", []):
        if "statisticalConfidence" not in pattern or not pattern.get("supportingEvidence") or pattern.get("reusable") is not True:
            issues.append("each pattern must include confidence, evidence, and reusable=true")
            break
    kb = data.get("executiveKnowledgeBase", {})
    for key in ["knowledgeIndexed", "searchSupported", "crossReferenced", "versionControlled"]:
        if kb.get(key) is not True:
            issues.append(f"executiveKnowledgeBase.{key} must be true")
    reuse = data.get("knowledgeReuse", {})
    for key in ["similarProjectsDetected", "relevantKnowledgeSuggested", "reuseExplained", "founderOverrideSupported"]:
        if not reuse.get(key):
            issues.append(f"knowledgeReuse.{key} is required")
    report = data.get("intelligenceReport", {})
    for key in ["newLessons", "updatedBusinessPatterns", "decisionAccuracy", "mostValuableInsights", "commonFailures", "recommendedImprovements"]:
        if not report.get(key):
            issues.append(f"intelligenceReport.{key} is required")
    availability = data.get("departmentAvailability", {})
    for key in ["availableToAllDepartments", "historicalContextAutomaticallyRetrieved", "learningVisibleInExecutiveDashboard", "organizationalMemoryVersionUpdated"]:
        if availability.get(key) is not True:
            issues.append(f"departmentAvailability.{key} must be true")
    score = data.get("overallScore")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("overallScore must be 0-100")
    return issues


def validate_organizational_intelligence_report(path: Path) -> list[str]:
    return validate_organizational_intelligence_report_payload(json.loads(path.read_text(encoding="utf-8")))


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0] if argv else sys.argv[1] if len(sys.argv) > 1 else "testing/fixtures/sample-organizational-intelligence-report.json")
    issues = validate_organizational_intelligence_report(path)
    if issues:
        print("FAIL: organizational intelligence report validation failed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"PASS: {path} is a valid Genesis organizational intelligence report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

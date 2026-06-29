#!/usr/bin/env python3
"""Sprint 2 executable vertical-slice acceptance test."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore

ACCEPTANCE_IDEA = "Create a coffee lovers product brand for India."
REQUIRED_REPORT_KEYS = [
    "trendAnalysis",
    "competitorAnalysis",
    "customerAnalysis",
    "productResearch",
    "overallScore",
    "recommendation",
    "risks",
    "nextActions",
]


def run_e2e(data_dir: str | Path | None = None) -> dict[str, object]:
    """Run founder idea -> persisted research report e2e flow."""

    if data_dir is None:
        with tempfile.TemporaryDirectory() as directory:
            return run_e2e(directory)

    store = JsonStore(data_dir)
    result = GenesisOrchestrator(store).submit_idea(ACCEPTANCE_IDEA)
    project = result["project"]
    workflow = result["workflow"]
    report = store.get_report(project["id"])
    employee_outputs = store.list_employee_outputs(workflow["id"])

    issues: list[str] = []
    if project["status"] != "RESEARCH_COMPLETED":
        issues.append(f"project status should be RESEARCH_COMPLETED, got {project['status']}")
    if workflow["status"] != "COMPLETED":
        issues.append(f"workflow status should be COMPLETED, got {workflow['status']}")
    if report.get("reportType") != "RESEARCH_REPORT":
        issues.append("reportType should be RESEARCH_REPORT")
    for key in REQUIRED_REPORT_KEYS:
        if key not in report:
            issues.append(f"missing report key: {key}")
    if len(employee_outputs) != 4:
        issues.append(f"expected 4 employee outputs, got {len(employee_outputs)}")
    if report.get("overallScore", 0) <= 0:
        issues.append("overallScore must be positive")
    if not report.get("risks"):
        issues.append("risks must not be empty")
    if not report.get("nextActions"):
        issues.append("nextActions must not be empty")

    return {
        "ok": not issues,
        "issues": issues,
        "projectId": project["id"],
        "workflowId": workflow["id"],
        "report": report,
    }


def main() -> int:
    result = run_e2e()
    if not result["ok"]:
        print("FAIL: Sprint 2 e2e acceptance test failed")
        for issue in result["issues"]:  # type: ignore[index]
            print(f"- {issue}")
        return 1
    print("PASS: Sprint 2 e2e acceptance test passed")
    print(f"Project: {result['projectId']}")
    print(f"Workflow: {result['workflowId']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

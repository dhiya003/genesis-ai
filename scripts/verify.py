#!/usr/bin/env python3
"""Genesis Sprint 2 verification suite."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "apps/api/app.py",
    "apps/cli/main.py",
    "apps/orchestrator/genesis_orchestrator.py",
    "apps/research/department.py",
    "apps/research/providers.py",
    "apps/employees/research.py",
    "apps/workflow/engine.py",
    "apps/storage/json_store.py",
    "scripts/sprint2_e2e.py",
    "scripts/validate_launch_pack.py",
    "scripts/validate_research_report.py",
    "tests/test_sprint2_e2e.py",
    "tests/test_api_http_e2e.py",
    "tests/test_research_providers.py",
    "api/schemas/research-report-v2.schema.json",
    "testing/fixtures/sample-research-report-v2.json",
    "docs/sprint-2-run-guide.md",
    "docs/sprint-2-provider-guide.md",
]

JSON_PATHS = [
    "api/schemas/launch-pack.schema.json",
    "api/schemas/research-report-v2.schema.json",
    "testing/fixtures/sample-launch-pack.json",
    "testing/fixtures/sample-research-report-v2.json",
]

COMMANDS = [
    ([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "unit + integration + e2e tests"),
    ([sys.executable, "scripts/validate_launch_pack.py"], "launch pack validation"),
    ([sys.executable, "scripts/validate_research_report.py"], "research report validation"),
    ([sys.executable, "scripts/sprint2_e2e.py"], "Sprint 2 e2e acceptance"),
]


def check_required_paths() -> list[str]:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        print(f"FAIL: missing required Sprint 2 paths: {missing}")
    else:
        print("PASS: required Sprint 2 paths exist")
    return missing


def check_json_files() -> list[str]:
    invalid = []
    for path in JSON_PATHS:
        try:
            json.loads((ROOT / path).read_text(encoding="utf-8"))
        except Exception as exc:
            invalid.append(f"{path}: {exc}")
    if invalid:
        print(f"FAIL: invalid JSON: {invalid}")
    else:
        print("PASS: required JSON files parse")
    return invalid


def run_command(command: list[str], label: str) -> bool:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode == 0:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    return False


def main() -> int:
    print("Genesis Sprint 2 Verification Suite")
    failures: list[str] = []
    failures.extend(check_required_paths())
    failures.extend(check_json_files())
    for command, label in COMMANDS:
        if not run_command(command, label):
            failures.append(label)
    if failures:
        print("\nRESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

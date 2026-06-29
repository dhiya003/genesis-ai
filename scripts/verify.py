#!/usr/bin/env python3
"""Genesis AI verification suite.

Runs repository-level validation for Sprint 1 foundation assets.
This script intentionally uses Python standard library only.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    ".env.example",
    "infrastructure/docker-compose.yml",
    "api/openapi.yaml",
    "database/schema.sql",
    "database/migrations/001_initial_schema.sql",
    "database/seeds/001_departments.sql",
    "database/seeds/002_employees.sql",
    "database/er-diagram.mmd",
    "architecture/system-context.mmd",
    "architecture/c4-container.mmd",
    "architecture/component-diagram.mmd",
    "architecture/sequences/research-workflow.mmd",
    "architecture/sequences/publishing-workflow.mmd",
    "architecture/state-machines/project-state.mmd",
    "architecture/state-machines/workflow-state.mmd",
    "prompts/ceo-ai-system.md",
    "prompts/product-factory-agent.md",
    "prompts/orchestrator/genesis-orchestrator.md",
    "prompts/research/emp-001-trend-research-specialist.md",
    "prompts/research/emp-002-competitor-research-specialist.md",
    "prompts/research/emp-003-customer-research-specialist.md",
    "prompts/research/emp-004-product-research-specialist.md",
    "testing/prompt-regression/research-trend-cases.json",
    "testing/prompt-regression/prompt-evaluation-checklist.md",
    "testing/fixtures/sample-project.json",
    "testing/fixtures/sample-trend-report.json",
    "testing/fixtures/sample-product-blueprint.json",
    "testing/fixtures/sample-creative-pack.json",
    "testing/fixtures/sample-marketing-pack.json",
    "docs/local-development.md",
    "docs/sprint-1d-completion.md",
    "docs/sprint-1-execution-validation.md",
    "docs/adr/001-product-factory-first.md",
    "implementation/sprint-2-plan.md",
]

JSON_FILES = [
    "api/schemas/research-report.schema.json",
    "api/schemas/product-blueprint.schema.json",
    "api/schemas/creative-pack.schema.json",
    "api/schemas/marketing-pack.schema.json",
    "api/schemas/publishing-package.schema.json",
    "api/schemas/analytics-report.schema.json",
    "api/schemas/error-response.schema.json",
    "testing/prompt-regression/research-trend-cases.json",
    "testing/fixtures/sample-project.json",
    "testing/fixtures/sample-trend-report.json",
    "testing/fixtures/sample-product-blueprint.json",
    "testing/fixtures/sample-creative-pack.json",
    "testing/fixtures/sample-marketing-pack.json",
]


def pass_msg(message: str) -> None:
    print(f"PASS: {message}")


def fail_msg(message: str) -> None:
    print(f"FAIL: {message}")


def check_required_files() -> list[str]:
    missing = []
    for rel_path in REQUIRED_FILES:
        if not (ROOT / rel_path).is_file():
            missing.append(rel_path)
    if missing:
        fail_msg(f"Missing required files: {missing}")
    else:
        pass_msg("All required Sprint 1 files are present")
    return missing


def check_json_syntax() -> list[str]:
    invalid = []
    for rel_path in JSON_FILES:
        path = ROOT / rel_path
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # noqa: BLE001
            invalid.append(f"{rel_path}: {exc}")
    if invalid:
        fail_msg(f"Invalid JSON files: {invalid}")
    else:
        pass_msg("All JSON files parse successfully")
    return invalid


def check_openapi_basic() -> list[str]:
    path = ROOT / "api/openapi.yaml"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_tokens = ["openapi:", "info:", "paths:", "components:"]
    missing = [token for token in required_tokens if token not in text]
    if missing:
        fail_msg(f"OpenAPI file missing required sections: {missing}")
    else:
        pass_msg("OpenAPI file contains required top-level sections")
    return missing


def check_schema_fixture_alignment() -> list[str]:
    issues = []
    fixture_to_report_type = {
        "testing/fixtures/sample-product-blueprint.json": "PRODUCT_BLUEPRINT",
        "testing/fixtures/sample-creative-pack.json": "CREATIVE_PACK",
        "testing/fixtures/sample-marketing-pack.json": "MARKETING_PACK",
    }
    for rel_path, expected_report_type in fixture_to_report_type.items():
        data = json.loads((ROOT / rel_path).read_text(encoding="utf-8"))
        actual = data.get("reportType")
        if actual != expected_report_type:
            issues.append(f"{rel_path}: expected {expected_report_type}, got {actual}")
    if issues:
        fail_msg(f"Fixture alignment issues: {issues}")
    else:
        pass_msg("Core fixtures align with expected report types")
    return issues


def check_optional_docker() -> int:
    docker = shutil.which("docker")
    if not docker:
        print("SKIP: Docker not available in this environment")
        return 0
    compose_file = ROOT / "infrastructure/docker-compose.yml"
    result = subprocess.run(
        [docker, "compose", "-f", str(compose_file), "config"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        pass_msg("Docker Compose configuration is valid")
    else:
        fail_msg("Docker Compose configuration failed validation")
        print(result.stdout)
        print(result.stderr)
    return result.returncode


def main() -> int:
    print("Genesis AI Sprint 1 Verification Suite")
    print(f"Repository root: {ROOT}")

    failures = []
    failures.extend(check_required_files())
    failures.extend(check_json_syntax())
    failures.extend(check_openapi_basic())
    failures.extend(check_schema_fixture_alignment())

    docker_status = check_optional_docker()
    if docker_status != 0:
        failures.append("Docker Compose validation failed")

    if failures:
        print("\nRESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

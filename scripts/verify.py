#!/usr/bin/env python3
"""Genesis AI verification suite.

Runs repository-level validation for Sprint 1 foundation assets and Sprint 2
vertical-slice assets. This script intentionally uses Python standard library only.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "CHANGELOG.md", ".env.example",
    "infrastructure/docker-compose.yml", "api/openapi.yaml", "database/schema.sql",
    "database/migrations/001_initial_schema.sql", "database/seeds/001_departments.sql",
    "database/seeds/002_employees.sql", "database/er-diagram.mmd",
    "architecture/system-context.mmd", "architecture/c4-container.mmd", "architecture/component-diagram.mmd",
    "architecture/sequences/research-workflow.mmd", "architecture/sequences/publishing-workflow.mmd",
    "architecture/state-machines/project-state.mmd", "architecture/state-machines/workflow-state.mmd",
    "prompts/ceo-ai-system.md", "prompts/product-factory-agent.md",
    "prompts/orchestrator/genesis-orchestrator.md",
    "prompts/research/emp-001-trend-research-specialist.md",
    "prompts/research/emp-002-competitor-research-specialist.md",
    "prompts/research/emp-003-customer-research-specialist.md",
    "prompts/research/emp-004-product-research-specialist.md",
    "testing/prompt-regression/research-trend-cases.json",
    "testing/prompt-regression/prompt-evaluation-checklist.md",
    "testing/fixtures/sample-project.json", "testing/fixtures/sample-trend-report.json",
    "testing/fixtures/sample-product-blueprint.json", "testing/fixtures/sample-creative-pack.json",
    "testing/fixtures/sample-marketing-pack.json", "docs/local-development.md",
    "docs/sprint-1d-completion.md", "docs/sprint-1-execution-validation.md",
    "docs/adr/001-product-factory-first.md", "implementation/sprint-2-plan.md",
]

SPRINT2_FILES = [
    "apps/__init__.py", "apps/api/__init__.py", "apps/api/app.py",
    "apps/worker/__init__.py", "apps/worker/main.py", "apps/cli/__init__.py", "apps/cli/main.py",
    "apps/errors.py", "apps/storage/__init__.py", "apps/storage/json_store.py",
    "apps/workflow/__init__.py", "apps/workflow/engine.py",
    "apps/employees/__init__.py", "apps/employees/research.py",
    "apps/research/__init__.py", "apps/research/department.py",
    "apps/orchestrator/__init__.py", "apps/orchestrator/genesis_orchestrator.py",
    "config/__init__.py", "config/runtime.py", "config/logging.py",
    "tests/test_runtime_bootstrap.py", "tests/test_product_factory_runner.py",
    "tests/test_workflow_engine.py", "tests/test_research_department.py", "tests/test_api_cli_research.py",
    "tests/test_sprint2_e2e.py", "scripts/sprint2_e2e.py", "scripts/validate_launch_pack.py",
    "docs/runtime-bootstrap.md", "docs/sprint-2-run-guide.md",
    "api/schemas/launch-pack.schema.json", "api/schemas/research-report-v2.schema.json",
    "testing/fixtures/sample-launch-pack.json", "testing/fixtures/sample-research-report-v2.json",
    "implementation/manual-ops/launch-checklist.md",
    "implementation/manual-ops/lead-tracker-template.csv",
    "implementation/manual-ops/validation-scorecard.md",
    "implementation/automation-hooks/phase-2-hook-registry.md",
]

JSON_FILES = [
    "api/schemas/research-report.schema.json", "api/schemas/product-blueprint.schema.json",
    "api/schemas/creative-pack.schema.json", "api/schemas/marketing-pack.schema.json",
    "api/schemas/publishing-package.schema.json", "api/schemas/analytics-report.schema.json",
    "api/schemas/error-response.schema.json", "api/schemas/launch-pack.schema.json",
    "api/schemas/research-report-v2.schema.json",
    "testing/prompt-regression/research-trend-cases.json",
    "testing/prompt-regression/product-factory-runner-cases.json",
    "testing/fixtures/sample-project.json", "testing/fixtures/sample-trend-report.json",
    "testing/fixtures/sample-product-blueprint.json", "testing/fixtures/sample-creative-pack.json",
    "testing/fixtures/sample-marketing-pack.json", "testing/fixtures/sample-launch-pack.json",
    "testing/fixtures/sample-research-report-v2.json",
]


def pass_msg(message: str) -> None:
    print(f"PASS: {message}")


def fail_msg(message: str) -> None:
    print(f"FAIL: {message}")


def check_files(paths: list[str], label: str) -> list[str]:
    missing = [rel_path for rel_path in paths if not (ROOT / rel_path).is_file()]
    if missing:
        fail_msg(f"Missing {label} files: {missing}")
    else:
        pass_msg(f"All {label} files are present")
    return missing


def check_json_syntax() -> list[str]:
    invalid = []
    for rel_path in JSON_FILES:
        try:
            json.loads((ROOT / rel_path).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            invalid.append(f"{rel_path}: {exc}")
    if invalid:
        fail_msg(f"Invalid JSON files: {invalid}")
    else:
        pass_msg("All JSON files parse successfully")
    return invalid


def check_openapi_basic() -> list[str]:
    text = (ROOT / "api/openapi.yaml").read_text(encoding="utf-8")
    required_tokens = ["openapi:", "info:", "paths:", "components:"]
    missing = [token for token in required_tokens if token not in text]
    if missing:
        fail_msg(f"OpenAPI file missing required sections: {missing}")
    else:
        pass_msg("OpenAPI file contains required top-level sections")
    return missing


def run_command(command: list[str], label: str) -> int:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    print(result.stdout)
    print(result.stderr)
    if result.returncode == 0:
        pass_msg(label)
    else:
        fail_msg(label)
    return result.returncode


def check_optional_docker() -> int:
    docker = shutil.which("docker")
    if not docker:
        print("SKIP: Docker not available in this environment")
        return 0
    return run_command([docker, "compose", "-f", "infrastructure/docker-compose.yml", "config"], "Docker Compose configuration is valid")


def main() -> int:
    print("Genesis AI Verification Suite")
    print(f"Repository root: {ROOT}")

    failures: list[str] = []
    failures.extend(check_files(REQUIRED_FILES, "Sprint 1 foundation"))
    failures.extend(check_files(SPRINT2_FILES, "Sprint 2 vertical-slice"))
    failures.extend(check_json_syntax())
    failures.extend(check_openapi_basic())

    if run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "Unit and integration tests pass") != 0:
        failures.append("Unit and integration tests failed")
    if run_command([sys.executable, "scripts/validate_launch_pack.py"], "Launch pack fixture validates") != 0:
        failures.append("Launch pack validation failed")
    if run_command([sys.executable, "scripts/sprint2_e2e.py"], "Sprint 2 e2e acceptance test passes") != 0:
        failures.append("Sprint 2 e2e acceptance test failed")
    if check_optional_docker() != 0:
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

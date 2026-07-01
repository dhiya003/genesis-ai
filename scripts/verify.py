#!/usr/bin/env python3
"""Genesis verification suite."""

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
    "apps/product/department.py",
    "apps/creative/department.py",
    "apps/marketing/department.py",
    "apps/sales/department.py",
    "apps/publishing/department.py",
    "apps/businessos/runtime.py",
    "apps/analytics/runtime.py",
    "apps/intelligence/runtime.py",
    "apps/enterprise/runtime.py",
    "apps/dashboard.py",
    "apps/security.py",
    "apps/founder/management.py",
    "apps/project/lifecycle.py",
    "apps/integrations/registry.py",
    "apps/employees/research.py",
    "apps/workflow/engine.py",
    "apps/storage/json_store.py",
    "scripts/sprint2_e2e.py",
    "scripts/validate_launch_pack.py",
    "scripts/validate_research_report.py",
    "scripts/validate_product_definition.py",
    "scripts/validate_product_blueprint.py",
    "scripts/validate_creative_pack.py",
    "scripts/validate_marketing_pack.py",
    "scripts/validate_sales_package.py",
    "scripts/validate_business_launch_package.py",
    "scripts/validate_business_intelligence_report.py",
    "scripts/validate_business_operating_plan.py",
    "scripts/validate_organizational_intelligence_report.py",
    "scripts/validate_simulation_report.py",
    "scripts/validate_executive_planning_report.py",
    "scripts/validate_opportunity_discovery_report.py",
    "scripts/validate_execution_optimization_report.py",
    "scripts/validate_enterprise_organization.py",
    "scripts/validate_enterprise_integration_platform.py",
    "tests/test_sprint2_e2e.py",
    "tests/test_api_http_e2e.py",
    "tests/test_research_providers.py",
    "tests/test_product_department.py",
    "tests/test_product_blueprint.py",
    "tests/test_creative_pack.py",
    "tests/test_marketing_pack.py",
    "tests/test_sales_department.py",
    "tests/test_publishing_engine.py",
    "tests/test_businessos_runtime.py",
    "tests/test_analytics_runtime.py",
    "tests/test_v2_intelligence.py",
    "tests/test_production_guardrails.py",
    "tests/test_founder_management.py",
    "tests/test_project_lifecycle.py",
    "api/schemas/research-report-v2.schema.json",
    "api/schemas/product-definition.schema.json",
    "api/schemas/product-blueprint.schema.json",
    "api/schemas/creative-pack.schema.json",
    "api/schemas/marketing-pack.schema.json",
    "api/schemas/sales-package.schema.json",
    "testing/fixtures/sample-research-report-v2.json",
    "testing/fixtures/sample-product-definition.json",
    "testing/fixtures/sample-product-blueprint.json",
    "testing/fixtures/sample-creative-pack.json",
    "testing/fixtures/sample-marketing-pack.json",
    "testing/fixtures/sample-sales-package.json",
    "testing/fixtures/sample-business-launch-package.json",
    "testing/fixtures/sample-business-intelligence-report.json",
    "testing/fixtures/sample-business-operating-plan.json",
    "testing/fixtures/sample-organizational-intelligence-report.json",
    "testing/fixtures/sample-simulation-report.json",
    "testing/fixtures/sample-executive-planning-report.json",
    "testing/fixtures/sample-opportunity-discovery-report.json",
    "testing/fixtures/sample-execution-optimization-report.json",
    "testing/fixtures/sample-enterprise-organization.json",
    "testing/fixtures/sample-enterprise-integration-platform.json",
    "docs/sprint-2-run-guide.md",
    "docs/sprint-2-provider-guide.md",
    "docs/sprint-3-kickoff.md",
    "docs/sprint-3-phase-1-product-definition.md",
    "docs/sprint-4-definition-of-done.md",
    "docs/sprint-5-definition-of-done.md",
    "docs/sprint-6-definition-of-done.md",
    "docs/sprint-7-kickoff.md",
    "docs/sprint-8-definition-of-done.md",
    "docs/epic-01-business-founder-management.md",
    "docs/epic-02-04-lifecycle-validation.md",
    "docs/epic-05-research-intelligence-validation.md",
    "docs/epic-06-08-product-creative-validation.md",
    "docs/epic-09-10-marketing-sales-validation.md",
    "docs/epic-11-13-commerce-bi-executive-validation.md",
    "docs/epic-14-16-v2-intelligence-validation.md",
    "docs/epic-17-19-v2-v3-validation.md",
    "docs/epic-20-enterprise-integration-platform.md",
    "database/migrations/0002_epic_01_founder_business_management.sql",
    "database/migrations/0003_project_workflow_lifecycle.sql",
]

JSON_PATHS = [
    "api/schemas/launch-pack.schema.json",
    "api/schemas/research-report-v2.schema.json",
    "api/schemas/product-definition.schema.json",
    "api/schemas/product-blueprint.schema.json",
    "api/schemas/creative-pack.schema.json",
    "api/schemas/marketing-pack.schema.json",
    "api/schemas/sales-package.schema.json",
    "testing/fixtures/sample-launch-pack.json",
    "testing/fixtures/sample-research-report-v2.json",
    "testing/fixtures/sample-product-definition.json",
    "testing/fixtures/sample-product-blueprint.json",
    "testing/fixtures/sample-creative-pack.json",
    "testing/fixtures/sample-marketing-pack.json",
    "testing/fixtures/sample-sales-package.json",
    "testing/fixtures/sample-business-launch-package.json",
    "testing/fixtures/sample-business-intelligence-report.json",
    "testing/fixtures/sample-business-operating-plan.json",
    "testing/fixtures/sample-organizational-intelligence-report.json",
    "testing/fixtures/sample-simulation-report.json",
    "testing/fixtures/sample-executive-planning-report.json",
    "testing/fixtures/sample-opportunity-discovery-report.json",
    "testing/fixtures/sample-execution-optimization-report.json",
    "testing/fixtures/sample-enterprise-organization.json",
    "testing/fixtures/sample-enterprise-integration-platform.json",
]

COMMANDS = [
    ([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "unit + integration + e2e tests"),
    ([sys.executable, "scripts/validate_launch_pack.py"], "launch pack validation"),
    ([sys.executable, "scripts/validate_research_report.py"], "research report validation"),
    ([sys.executable, "scripts/validate_product_definition.py"], "product definition validation"),
    ([sys.executable, "scripts/validate_product_blueprint.py"], "product blueprint validation"),
    ([sys.executable, "scripts/validate_creative_pack.py"], "creative pack validation"),
    ([sys.executable, "scripts/validate_marketing_pack.py"], "marketing pack validation"),
    ([sys.executable, "scripts/validate_sales_package.py"], "sales package validation"),
    ([sys.executable, "scripts/validate_business_launch_package.py"], "business launch package validation"),
    ([sys.executable, "scripts/validate_business_intelligence_report.py"], "business intelligence report validation"),
    ([sys.executable, "scripts/validate_business_operating_plan.py"], "business operating plan validation"),
    ([sys.executable, "scripts/validate_organizational_intelligence_report.py"], "organizational intelligence report validation"),
    ([sys.executable, "scripts/validate_simulation_report.py"], "simulation report validation"),
    ([sys.executable, "scripts/validate_executive_planning_report.py"], "executive planning report validation"),
    ([sys.executable, "scripts/validate_opportunity_discovery_report.py"], "opportunity discovery report validation"),
    ([sys.executable, "scripts/validate_execution_optimization_report.py"], "execution optimization report validation"),
    ([sys.executable, "scripts/validate_enterprise_organization.py"], "enterprise organization validation"),
    ([sys.executable, "scripts/validate_enterprise_integration_platform.py"], "enterprise integration platform validation"),
    ([sys.executable, "scripts/sprint2_e2e.py"], "Sprint 2 e2e acceptance"),
]


def check_required_paths() -> list[str]:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        print(f"FAIL: missing required Genesis paths: {missing}")
    else:
        print("PASS: required Genesis paths exist")
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
    print("Genesis Verification Suite")
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

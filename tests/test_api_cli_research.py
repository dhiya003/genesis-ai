"""API and CLI tests for persisted research report retrieval."""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from apps.api.app import GenesisApiHandler
from apps.cli.main import main as cli_main
from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore


class ApiCliResearchTests(unittest.TestCase):
    def test_cli_submit_then_report_retrieves_persisted_research_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = StringIO()
            with patch("sys.stdout", output):
                self.assertEqual(cli_main(["submit", "Create a coffee lovers product brand for India.", "--data-dir", directory]), 0)
            submit_payload = json.loads(output.getvalue())
            project_id = submit_payload["project"]["id"]

            project_output = StringIO()
            with patch("sys.stdout", project_output):
                self.assertEqual(cli_main(["project", project_id, "--data-dir", directory]), 0)
            project_payload = json.loads(project_output.getvalue())
            self.assertEqual(project_payload["project"]["id"], project_id)
            self.assertTrue(project_payload["tasks"])
            self.assertTrue(project_payload["deliverables"])

            report_output = StringIO()
            with patch("sys.stdout", report_output):
                self.assertEqual(cli_main(["report", project_id, "--data-dir", directory]), 0)
            report = json.loads(report_output.getvalue())
            self.assertEqual(report["reportType"], "RESEARCH_REPORT")
            self.assertEqual(report["projectId"], project_id)
            self.assertIn("recommendation", report)
            self.assertIn("executiveSummary", report)

            version_output = StringIO()
            with patch("sys.stdout", version_output):
                self.assertEqual(cli_main(["version"]), 0)
            self.assertEqual(json.loads(version_output.getvalue())["version"], "1.0.0-foundation")

            product_output = StringIO()
            with patch("sys.stdout", product_output):
                self.assertEqual(cli_main(["product", "run", project_id, "--data-dir", directory]), 0)
            product_run = json.loads(product_output.getvalue())
            self.assertEqual(product_run["productDefinition"]["reportType"], "PRODUCT_DEFINITION")
            self.assertEqual(product_run["productDefinition"]["projectId"], project_id)

            product_definition_output = StringIO()
            with patch("sys.stdout", product_definition_output):
                self.assertEqual(cli_main(["product", "definition", project_id, "--data-dir", directory]), 0)
            product_definition = json.loads(product_definition_output.getvalue())
            self.assertEqual(product_definition["reportType"], "PRODUCT_DEFINITION")
            self.assertEqual(product_definition["projectId"], project_id)

            product_blueprint_output = StringIO()
            with patch("sys.stdout", product_blueprint_output):
                self.assertEqual(cli_main(["product", "generate", project_id, "--data-dir", directory]), 0)
            product_blueprint_run = json.loads(product_blueprint_output.getvalue())
            self.assertEqual(product_blueprint_run["blueprint"]["reportType"], "PRODUCT_BLUEPRINT")

            product_bom_output = StringIO()
            with patch("sys.stdout", product_bom_output):
                self.assertEqual(cli_main(["product", "bom", project_id, "--data-dir", directory]), 0)
            self.assertTrue(json.loads(product_bom_output.getvalue())["items"])

            product_cost_output = StringIO()
            with patch("sys.stdout", product_cost_output):
                self.assertEqual(cli_main(["product", "cost", project_id, "--data-dir", directory]), 0)
            self.assertGreater(json.loads(product_cost_output.getvalue())["landedCost"], 0)

            creative_output = StringIO()
            with patch("sys.stdout", creative_output):
                self.assertEqual(cli_main(["creative", "generate", project_id, "--data-dir", directory]), 0)
            creative_run = json.loads(creative_output.getvalue())
            self.assertEqual(creative_run["creativePack"]["reportType"], "CREATIVE_PACK")

            creative_brand_output = StringIO()
            with patch("sys.stdout", creative_brand_output):
                self.assertEqual(cli_main(["creative", "brand", project_id, "--data-dir", directory]), 0)
            self.assertTrue(json.loads(creative_brand_output.getvalue())["brandName"])

            marketing_output = StringIO()
            with patch("sys.stdout", marketing_output):
                self.assertEqual(cli_main(["marketing", "generate", project_id, "--data-dir", directory]), 0)
            marketing_run = json.loads(marketing_output.getvalue())
            self.assertEqual(marketing_run["marketingPack"]["reportType"], "MARKETING_PACK")

            marketing_seo_output = StringIO()
            with patch("sys.stdout", marketing_seo_output):
                self.assertEqual(cli_main(["marketing", "seo", project_id, "--data-dir", directory]), 0)
            self.assertTrue(json.loads(marketing_seo_output.getvalue())["keywords"])

            launch_output = StringIO()
            with patch("sys.stdout", launch_output):
                self.assertEqual(cli_main(["launch", "generate", project_id, "--data-dir", directory]), 0)
            launch_run = json.loads(launch_output.getvalue())
            self.assertEqual(launch_run["businessLaunchPackage"]["reportType"], "BUSINESS_LAUNCH_PACKAGE")

            launch_status_output = StringIO()
            with patch("sys.stdout", launch_status_output):
                self.assertEqual(cli_main(["launch", "status", project_id, "--data-dir", directory]), 0)
            self.assertIn(json.loads(launch_status_output.getvalue())["status"], {"READY_FOR_FOUNDER_APPROVAL", "NEEDS_REVIEW"})

            businessos_output = StringIO()
            with patch("sys.stdout", businessos_output):
                self.assertEqual(cli_main(["businessos", "generate", project_id, "--data-dir", directory]), 0)
            businessos_run = json.loads(businessos_output.getvalue())
            self.assertEqual(businessos_run["businessOperatingPlan"]["reportType"], "BUSINESS_OPERATING_PLAN")

            health_output = StringIO()
            with patch("sys.stdout", health_output):
                self.assertEqual(cli_main(["businessos", "health", project_id, "--data-dir", directory]), 0)
            self.assertGreaterEqual(json.loads(health_output.getvalue())["overallBusinessHealthScore"], 0)

    def test_api_handler_uses_same_store_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            result = GenesisOrchestrator(store).submit_idea("Create a coffee lovers product brand for India.")
            project_id = result["project"]["id"]
            report = store.get_report(project_id)
            self.assertEqual(report["projectId"], project_id)
            self.assertTrue(hasattr(GenesisApiHandler, "do_GET"))
            self.assertTrue(hasattr(GenesisApiHandler, "do_POST"))


if __name__ == "__main__":
    unittest.main()

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
            self.assertEqual(json.loads(version_output.getvalue())["version"], "0.3.0")

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

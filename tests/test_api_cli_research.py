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

            report_output = StringIO()
            with patch("sys.stdout", report_output):
                self.assertEqual(cli_main(["report", project_id, "--data-dir", directory]), 0)
            report = json.loads(report_output.getvalue())
            self.assertEqual(report["reportType"], "RESEARCH_REPORT")
            self.assertEqual(report["projectId"], project_id)
            self.assertIn("recommendation", report)

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

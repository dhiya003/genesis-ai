"""Tests for Sprint 2 approval, recovery, and observability additions."""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from apps.cli.main import main as cli_main
from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore


class ApprovalObservabilityTests(unittest.TestCase):
    def test_manual_approval_gate_can_be_approved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            result = GenesisOrchestrator(store).submit_idea("Create a coffee lovers product brand for India.", approval_mode="manual")

            self.assertEqual(result["project"]["status"], "AWAITING_APPROVAL")
            self.assertEqual(result["approval"]["status"], "PENDING")

            approved = GenesisOrchestrator(store).approve_gate(result["approval"]["id"], actor="founder", note="Looks good.")

            self.assertEqual(approved["approval"]["status"], "APPROVED")
            self.assertEqual(approved["project"]["status"], "RESEARCH_APPROVED")

    def test_submit_records_metrics_and_cli_can_list_them(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = StringIO()
            with patch("sys.stdout", output):
                self.assertEqual(cli_main(["submit", "Create a coffee lovers product brand for India.", "--data-dir", directory]), 0)

            metrics_output = StringIO()
            with patch("sys.stdout", metrics_output):
                self.assertEqual(cli_main(["metrics", "--data-dir", directory]), 0)

            payload = json.loads(metrics_output.getvalue())
            metric_types = {metric["type"] for metric in payload["metrics"]}
            self.assertIn("workflow.completed", metric_types)
            self.assertIn("employee.completed", metric_types)
            self.assertIn("summary", payload)
            self.assertGreaterEqual(payload["summary"]["eventCount"], 1)


if __name__ == "__main__":
    unittest.main()

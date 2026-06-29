"""Tests for Research Department and Genesis Orchestrator."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore


class ResearchDepartmentTests(unittest.TestCase):
    def test_orchestrator_runs_research_department_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            result = orchestrator.submit_idea("Create a coffee lovers product brand for India.")
            report = result["report"]
            self.assertEqual(result["project"]["status"], "RESEARCH_COMPLETED")
            self.assertEqual(result["workflow"]["status"], "COMPLETED")
            self.assertEqual(report["reportType"], "RESEARCH_REPORT")
            self.assertIn("trendAnalysis", report)
            self.assertIn("competitorAnalysis", report)
            self.assertIn("customerAnalysis", report)
            self.assertIn("productResearch", report)
            self.assertGreaterEqual(report["overallScore"], 1)
            self.assertTrue(report["recommendation"])
            self.assertEqual(len(store.list_employee_outputs(result["workflow"]["id"])), 4)
            self.assertEqual(store.get_report(result["project"]["id"])["projectId"], result["project"]["id"])


if __name__ == "__main__":
    unittest.main()

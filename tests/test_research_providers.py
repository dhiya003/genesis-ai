"""Tests for research provider contract."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from apps.employees import EMPLOYEES, run_employee
from apps.research.providers import DeterministicResearchProvider, get_research_provider


class ResearchProviderTests(unittest.TestCase):
    def test_deterministic_provider_executes_all_research_employees(self) -> None:
        provider = DeterministicResearchProvider()
        project = {"id": "project-1", "workflowId": "workflow-1", "idea": "Create a coffee lovers product brand for India."}
        sections = []
        for employee_id in EMPLOYEES:
            output = run_employee(employee_id, project, provider=provider)
            sections.append(output["section"])
            self.assertEqual(output["status"], "COMPLETED")
            self.assertEqual(output["projectId"], "project-1")
            self.assertGreaterEqual(output["score"], 0)
            self.assertLessEqual(output["score"], 100)
        self.assertEqual(sorted(sections), sorted(["trendAnalysis", "competitorAnalysis", "customerAnalysis", "productResearch"]))

    def test_provider_defaults_to_deterministic_without_external_credentials(self) -> None:
        with patch.dict(os.environ, {"GENESIS_RESEARCH_PROVIDER": "deterministic"}, clear=False):
            self.assertIsInstance(get_research_provider(), DeterministicResearchProvider)

    def test_openai_provider_requires_api_key(self) -> None:
        with patch.dict(os.environ, {"GENESIS_RESEARCH_PROVIDER": "openai"}, clear=True):
            with self.assertRaises(RuntimeError):
                get_research_provider()


if __name__ == "__main__":
    unittest.main()

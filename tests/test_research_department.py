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
            self.assertEqual(report["trendAnalysis"]["employeeId"], "EMP-001")
            self.assertTrue(report["trendAnalysis"]["growthDrivers"])
            self.assertEqual(report["competitorAnalysis"]["employeeId"], "EMP-002")
            self.assertTrue(report["competitorAnalysis"]["marketGaps"])
            self.assertEqual(report["customerAnalysis"]["employeeId"], "EMP-003")
            self.assertTrue(report["customerAnalysis"]["personas"])
            self.assertEqual(report["productResearch"]["employeeId"], "EMP-004")
            self.assertTrue(report["productResearch"]["rankedOpportunities"])
            self.assertGreaterEqual(report["overallScore"], 1)
            self.assertIn(report["opportunityRating"], {"Very Poor", "Poor", "Average", "Good", "Excellent"})
            self.assertTrue(report["opportunityScoring"]["weights"])
            self.assertTrue(report["riskAssessment"])
            self.assertTrue(all("mitigation" in risk for risk in report["riskAssessment"]))
            self.assertIn(report["executiveRecommendation"]["type"], {"Proceed", "Proceed with Caution", "Validate Further", "Pivot", "Do Not Proceed"})
            self.assertTrue(report["mergeSummary"]["sectionOwnership"])
            self.assertTrue(report["researchExecution"]["parallelExecutionSupported"])
            self.assertTrue(report["researchExecution"]["sequentialFallbackSupported"])
            self.assertTrue(all(item["status"] == "PASS" for item in report["completionChecklist"]))
            self.assertTrue(report["downstreamReadiness"]["productFactoryInputReady"])
            self.assertTrue(report["recommendation"])
            self.assertEqual(len(store.list_employee_outputs(result["workflow"]["id"])), 4)
            self.assertEqual(store.get_report(result["project"]["id"])["projectId"], result["project"]["id"])
            self.assertTrue(store.list_product_knowledge(project_id=result["project"]["id"]))


if __name__ == "__main__":
    unittest.main()

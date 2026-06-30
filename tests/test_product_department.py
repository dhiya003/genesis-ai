"""Product Department tests for Sprint 3."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from scripts.validate_product_definition import validate_product_definition_payload


class ProductDepartmentTests(unittest.TestCase):
    def test_orchestrator_runs_product_definition_from_research_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            research = orchestrator.submit_idea(
                "Create a coffee lovers product brand for India.",
                country="India",
                budget="50000 INR",
                timeline="14 days",
                constraints=["low MOQ"],
            )
            project_id = research["project"]["id"]

            result = orchestrator.run_product_definition(project_id)
            product_definition = result["productDefinition"]

            self.assertEqual(result["project"]["status"], "PRODUCT_DEFINITION_COMPLETED")
            self.assertEqual(product_definition["reportType"], "PRODUCT_DEFINITION")
            self.assertEqual(product_definition["projectId"], project_id)
            self.assertEqual(product_definition["department"], "PRODUCT")
            self.assertFalse(validate_product_definition_payload(product_definition))
            self.assertEqual(store.get_product_definition(project_id)["projectId"], project_id)
            self.assertTrue(store.list_product_knowledge(project_id=project_id))

            levels = {variant["level"] for variant in product_definition["variantMatrix"]}
            self.assertEqual(
                {"Starter", "Standard", "Premium", "Bundle", "Subscription", "Accessories", "Expansion Packs"},
                levels,
            )
            self.assertIn("overallOpportunityScore", product_definition["opportunityReport"])
            self.assertIn("overallProductScore", product_definition["successMetrics"])
            self.assertTrue(product_definition["opportunityReport"]["rejectedAlternatives"])


if __name__ == "__main__":
    unittest.main()

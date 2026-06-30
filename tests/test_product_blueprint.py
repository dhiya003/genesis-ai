"""Sprint 3 Product Blueprint tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.product.employees import PRODUCT_EMPLOYEES, run_product_employee, validate_product_employee_output
from apps.storage import JsonStore
from scripts.validate_product_blueprint import validate_product_blueprint_payload


class ProductBlueprintTests(unittest.TestCase):
    def test_product_employee_contracts_are_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            research = orchestrator.submit_idea("Build a premium educational wooden toy business for children aged 3-5 in India.")
            project = research["project"]
            workflow = {"id": "workflow-test"}
            product_definition = orchestrator.run_product_definition(project["id"])["productDefinition"]
            context = {"project": project, "workflow": workflow, "researchReport": research["report"], "productDefinition": product_definition, "sections": {}}

            for employee_id in PRODUCT_EMPLOYEES:
                output = run_product_employee(employee_id, context)
                self.assertFalse(validate_product_employee_output(output))
                context["sections"][output["section"]] = output

    def test_orchestrator_generates_complete_product_blueprint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            research = orchestrator.submit_idea(
                "Build a premium educational wooden toy business for children aged 3-5 in India.",
                country="India",
                budget="300000 INR",
                timeline="45 days",
                constraints=["premium wooden material", "low MOQ pilot"],
            )
            project_id = research["project"]["id"]

            result = orchestrator.generate_product_blueprint(project_id)
            blueprint = result["blueprint"]

            self.assertEqual(result["project"]["status"], "PRODUCT_BLUEPRINT_COMPLETED")
            self.assertEqual(blueprint["reportType"], "PRODUCT_BLUEPRINT")
            self.assertEqual(blueprint["productId"], project_id)
            self.assertFalse(validate_product_blueprint_payload(blueprint))
            self.assertEqual(store.get_product_blueprint(project_id)["productId"], project_id)
            self.assertTrue(store.get_bom_report(project_id)["items"])
            self.assertGreater(store.get_cost_report(project_id)["landedCost"], 0)
            self.assertTrue(store.get_supplier_report(project_id)["shortlist"])
            self.assertGreater(store.get_profitability_report(project_id)["profitPerUnit"], 0)
            self.assertTrue(store.get_manufacturing_plan(project_id)["manufacturingSequence"])

    def test_founder_acceptance_wooden_toy_business(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            research = orchestrator.submit_idea(
                "Build a premium educational wooden toy business for children aged 3-5 in India.",
                country="India",
                budget="300000 INR",
                timeline="45 days",
            )
            blueprint = orchestrator.generate_product_blueprint(research["project"]["id"])["blueprint"]

            variant_levels = {variant["level"] for variant in blueprint["productVariants"]}
            self.assertTrue({"Starter", "Standard", "Premium"}.issubset(variant_levels))
            self.assertIn("manufacturingTechnology", blueprint["manufacturingPlan"])
            self.assertTrue(blueprint["bom"]["items"])
            self.assertTrue(blueprint["materialRecommendation"]["primaryMaterials"])
            self.assertTrue(blueprint["packagingSpecification"]["packagingMaterials"])
            self.assertTrue(blueprint["supplierRecommendations"]["shortlist"])
            self.assertGreater(blueprint["costAnalysis"]["landedCost"], 0)
            self.assertGreater(blueprint["pricingStrategy"]["retailPrice"], blueprint["costAnalysis"]["landedCost"])
            self.assertGreater(blueprint["profitabilityReport"]["profitPerUnit"], 0)
            self.assertTrue(blueprint["risks"])
            self.assertTrue(blueprint["assumptions"])
            self.assertTrue(blueprint["launchReadyEngineeringPackage"]["readyForSupplierDiscussion"])


if __name__ == "__main__":
    unittest.main()

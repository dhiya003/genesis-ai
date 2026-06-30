"""Sprint 8 BusinessOS runtime foundation tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from scripts.validate_business_operating_plan import validate_business_operating_plan_payload


class BusinessOSRuntimeTests(unittest.TestCase):
    def _launch_flow(self, orchestrator: GenesisOrchestrator) -> dict[str, object]:
        research = orchestrator.submit_idea(
            "Build a premium educational wooden toy business for children aged 3-5 in India.",
            country="India",
            budget="300000 INR",
            timeline="45 days",
        )
        product_blueprint = orchestrator.generate_product_blueprint(research["project"]["id"])["blueprint"]
        creative_pack = orchestrator.generate_creative_pack(product_blueprint["productId"])["creativePack"]
        marketing_pack = orchestrator.generate_marketing_pack(creative_pack["creativeId"])["marketingPack"]
        return orchestrator.generate_business_launch_package(marketing_pack["marketingId"])["businessLaunchPackage"]

    def test_orchestrator_generates_business_operating_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            launch_package = self._launch_flow(orchestrator)

            result = orchestrator.generate_business_operating_plan(launch_package["launchId"])
            plan = result["businessOperatingPlan"]

            self.assertEqual(result["project"]["status"], "AWAITING_BUSINESS_OS_APPROVAL")
            self.assertEqual(plan["reportType"], "BUSINESS_OPERATING_PLAN")
            self.assertFalse(validate_business_operating_plan_payload(plan))
            self.assertEqual(store.get_business_operating_plan(plan["businessId"])["businessId"], plan["businessId"])
            self.assertTrue(store.get_digital_twin(plan["businessId"])["products"])
            self.assertTrue(store.get_knowledge_graph(plan["businessId"])["edges"])
            self.assertTrue(store.get_decision_register(plan["businessId"])["decisions"])
            self.assertTrue(store.get_simulation_report(plan["businessId"])["simulations"])
            self.assertGreaterEqual(store.get_business_health_report(plan["businessId"])["overallBusinessHealthScore"], 0)
            self.assertTrue(store.get_recommendation_report(plan["businessId"])["recommendations"])

    def test_founder_acceptance_businessos_has_closed_loop_governance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            launch_package = self._launch_flow(orchestrator)
            plan = orchestrator.generate_business_operating_plan(launch_package["launchId"])["businessOperatingPlan"]

            self.assertEqual(plan["runtime"], "Genesis CEO Runtime")
            self.assertIn("Research Again", plan["crossDepartmentLoop"])
            self.assertTrue(plan["executiveCouncil"])
            self.assertTrue(plan["departmentPlans"])
            self.assertTrue(plan["digitalTwin"]["products"])
            self.assertTrue(plan["businessMemory"]["projects"])
            self.assertTrue(plan["knowledgeGraph"]["nodes"])
            self.assertTrue(plan["simulationResults"])
            self.assertGreaterEqual(plan["businessHealth"]["overallBusinessHealthScore"], 0)
            self.assertTrue(plan["opportunities"])
            self.assertTrue(plan["risks"])
            self.assertTrue(plan["learningEngine"]["captures"])
            self.assertIn("No irreversible action without configured approval policy.", plan["governanceBoundaries"])


if __name__ == "__main__":
    unittest.main()

"""Sprint 6 Commerce & Publishing tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.publishing.employees import PUBLISHING_EMPLOYEES, run_publishing_employee, validate_publishing_employee_output
from apps.storage import JsonStore
from scripts.validate_business_launch_package import validate_business_launch_package_payload


class PublishingEngineTests(unittest.TestCase):
    def _marketing_flow(self, orchestrator: GenesisOrchestrator) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
        research = orchestrator.submit_idea(
            "Build a premium educational wooden toy business for children aged 3-5 in India.",
            country="India",
            budget="300000 INR",
            timeline="45 days",
        )
        product_blueprint = orchestrator.generate_product_blueprint(research["project"]["id"])["blueprint"]
        creative_pack = orchestrator.generate_creative_pack(product_blueprint["productId"])["creativePack"]
        marketing_pack = orchestrator.generate_marketing_pack(creative_pack["creativeId"])["marketingPack"]
        return research, product_blueprint, creative_pack, marketing_pack

    def test_publishing_employee_contracts_are_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            research, product_blueprint, creative_pack, marketing_pack = self._marketing_flow(orchestrator)
            context = {
                "project": research["project"],
                "workflow": {"id": "workflow-test"},
                "productBlueprint": product_blueprint,
                "creativePack": creative_pack,
                "marketingPack": marketing_pack,
                "sections": {},
            }

            for employee_id in PUBLISHING_EMPLOYEES:
                output = run_publishing_employee(employee_id, context)
                self.assertFalse(validate_publishing_employee_output(output))
                context["sections"][output["section"]] = output

    def test_orchestrator_generates_business_launch_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            _, _, _, marketing_pack = self._marketing_flow(orchestrator)

            result = orchestrator.generate_business_launch_package(marketing_pack["marketingId"])
            launch_package = result["businessLaunchPackage"]

            self.assertEqual(result["project"]["status"], "AWAITING_BUSINESS_LAUNCH_APPROVAL")
            self.assertEqual(launch_package["reportType"], "BUSINESS_LAUNCH_PACKAGE")
            self.assertEqual(launch_package["department"], "COMMERCE_AND_PUBLISHING")
            self.assertEqual(launch_package["departmentStatus"], "COMPLETED")
            self.assertFalse(validate_business_launch_package_payload(launch_package))
            self.assertEqual(store.get_business_launch_package(marketing_pack["marketingId"])["launchId"], marketing_pack["marketingId"])
            self.assertTrue(store.get_launch_checklist(marketing_pack["marketingId"])["checklist"])
            self.assertTrue(store.get_asset_manifest(marketing_pack["marketingId"])["assets"])
            self.assertTrue(store.get_publishing_plan(marketing_pack["marketingId"])["executionMode"])
            self.assertTrue(store.get_business_launch_report(marketing_pack["marketingId"])["channelsPrepared"])

    def test_founder_acceptance_launch_package_is_execution_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            _, _, _, marketing_pack = self._marketing_flow(orchestrator)
            launch_package = orchestrator.generate_business_launch_package(marketing_pack["marketingId"])["businessLaunchPackage"]

            self.assertTrue(launch_package["productCatalogue"]["items"])
            self.assertEqual(launch_package["productCatalogue"]["uniqueSkuCount"], len(launch_package["productCatalogue"]["items"]))
            self.assertTrue(launch_package["catalogueSearch"]["supported"])
            self.assertTrue(launch_package["catalogueVersionHistory"])
            self.assertTrue(launch_package["productLifecycle"])
            self.assertTrue(launch_package["channelsDetected"])
            self.assertTrue(launch_package["marketplacePublishingPlan"]["listings"])
            self.assertTrue(launch_package["socialPublishingPlan"]["channels"])
            self.assertEqual(launch_package["contentSchedule"]["timezone"], "Asia/Kolkata")
            self.assertTrue(launch_package["assetRepository"]["assets"])
            self.assertTrue(launch_package["storeManagementPlan"]["catalog"])
            self.assertTrue(launch_package["inventorySynchronization"]["negativeInventoryPrevented"])
            self.assertTrue(launch_package["pricingSynchronization"]["effectiveDatesSupported"])
            self.assertTrue(launch_package["campaignLaunchPlan"]["campaigns"])
            self.assertEqual(launch_package["campaignLaunchPlan"]["executionMode"], "APPROVAL_GATED_DRAFTS")
            self.assertTrue(launch_package["approvalPlan"]["approvalGates"])
            self.assertTrue(launch_package["notificationPlan"]["notifications"])
            self.assertTrue(launch_package["rollbackPlan"]["supportedActions"])
            self.assertTrue(launch_package["launchMonitoring"]["activeDuringLaunch"])
            self.assertGreaterEqual(launch_package["launchValidation"]["score"], 0)
            self.assertLessEqual(launch_package["launchValidation"]["score"], 100)
            self.assertIn(launch_package["launchStatus"], {"READY_FOR_FOUNDER_APPROVAL", "NEEDS_REVIEW"})
            self.assertTrue(launch_package["launchReport"]["remainingTasks"])
            self.assertEqual(launch_package["workflowTransition"], "BUSINESS_INTELLIGENCE")
            self.assertTrue(launch_package["departmentMetrics"])
            self.assertTrue(launch_package["knowledgeBaseEntries"])


if __name__ == "__main__":
    unittest.main()

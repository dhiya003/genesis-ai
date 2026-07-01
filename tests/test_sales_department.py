"""Sprint 6 AI Sales Department tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.sales.employees import SALES_EMPLOYEES, run_sales_employee, validate_sales_employee_output
from apps.storage import JsonStore
from scripts.validate_sales_package import validate_sales_package_payload


class SalesDepartmentTests(unittest.TestCase):
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

    def test_sales_employee_contracts_are_executable(self) -> None:
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

            for employee_id in SALES_EMPLOYEES:
                output = run_sales_employee(employee_id, context)
                self.assertFalse(validate_sales_employee_output(output))
                context["sections"][output["section"]] = output

    def test_orchestrator_generates_complete_sales_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            _, _, _, marketing_pack = self._marketing_flow(orchestrator)

            result = orchestrator.generate_sales_package(marketing_pack["marketingId"])
            sales_package = result["salesPackage"]

            self.assertEqual(result["project"]["status"], "SALES_PACKAGE_COMPLETED")
            self.assertEqual(sales_package["reportType"], "SALES_PACKAGE")
            self.assertFalse(validate_sales_package_payload(sales_package))
            self.assertEqual(store.get_sales_package(marketing_pack["marketingId"])["salesId"], marketing_pack["marketingId"])
            self.assertTrue(store.get_crm_report(marketing_pack["marketingId"])["customerRecords"])
            self.assertTrue(store.get_quotation_report(marketing_pack["marketingId"])["quotes"])
            self.assertTrue(store.get_sales_pipeline_report(marketing_pack["marketingId"])["opportunities"])
            self.assertTrue(store.get_order_handoff_report(marketing_pack["marketingId"])["orders"])
            self.assertTrue(store.get_sales_analytics_report(marketing_pack["marketingId"])["metrics"])

    def test_founder_acceptance_sales_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            _, _, _, marketing_pack = self._marketing_flow(orchestrator)
            sales_package = orchestrator.generate_sales_package(marketing_pack["marketingId"])["salesPackage"]

            self.assertEqual(sales_package["departmentStatus"], "COMPLETED")
            self.assertEqual(sales_package["salesDirector"]["employeeId"], "EMP-401")
            self.assertTrue(sales_package["communicationChannels"])
            self.assertTrue(sales_package["leadQualification"]["leads"])
            self.assertTrue(sales_package["leadQualification"]["duplicateLeads"])
            self.assertTrue(sales_package["salesConversations"]["conversationPlaybooks"])
            self.assertTrue(sales_package["salesConversations"]["escalationRules"])
            self.assertTrue(sales_package["quotations"]["quotes"])
            self.assertTrue(sales_package["quotations"]["versionHistory"])
            self.assertTrue(sales_package["followUpAutomation"]["followUpSchedules"])
            self.assertTrue(sales_package["followUpAutomation"]["stopConditions"])
            self.assertTrue(sales_package["crmSynchronization"]["customerRecords"])
            self.assertTrue(sales_package["salesPipeline"]["stageConfiguration"])
            self.assertTrue(sales_package["salesPipeline"]["transitionAudit"])
            self.assertTrue(sales_package["orderHandoff"]["orders"])
            self.assertTrue(sales_package["salesAnalytics"]["metrics"])
            self.assertEqual(sales_package["commercePublishingTransition"]["status"], "READY")
            self.assertTrue(sales_package["knowledgeBaseEntries"])


if __name__ == "__main__":
    unittest.main()

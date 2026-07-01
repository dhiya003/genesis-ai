"""Genesis v2/v3 intelligence, optimization, and enterprise tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from scripts.validate_enterprise_organization import validate_enterprise_organization_payload
from scripts.validate_execution_optimization_report import validate_execution_optimization_report_payload
from scripts.validate_executive_planning_report import validate_executive_planning_report_payload
from scripts.validate_organizational_intelligence_report import validate_organizational_intelligence_report_payload
from scripts.validate_opportunity_discovery_report import validate_opportunity_discovery_report_payload
from scripts.validate_simulation_report import validate_simulation_report_payload


class GenesisV2V3IntelligenceTests(unittest.TestCase):
    def _businessos_flow(self, orchestrator: GenesisOrchestrator) -> str:
        research = orchestrator.submit_idea(
            "Build a premium educational wooden toy business for children aged 3-5 in India.",
            country="India",
            budget="300000 INR",
            timeline="45 days",
        )
        product_blueprint = orchestrator.generate_product_blueprint(research["project"]["id"])["blueprint"]
        creative_pack = orchestrator.generate_creative_pack(product_blueprint["productId"])["creativePack"]
        marketing_pack = orchestrator.generate_marketing_pack(creative_pack["creativeId"])["marketingPack"]
        orchestrator.generate_sales_package(marketing_pack["marketingId"])
        launch_package = orchestrator.generate_business_launch_package(marketing_pack["marketingId"])["businessLaunchPackage"]
        orchestrator.generate_business_intelligence_report(launch_package["launchId"])
        return orchestrator.generate_business_operating_plan(launch_package["launchId"])["businessOperatingPlan"]["businessId"]

    def test_v2_and_v3_reports_cover_learning_simulation_planning_optimization_and_enterprise(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            business_id = self._businessos_flow(orchestrator)

            organizational = orchestrator.generate_organizational_intelligence_report(business_id)["organizationalIntelligenceReport"]
            simulation = orchestrator.generate_simulation_report(business_id)["simulationReport"]
            planning = orchestrator.generate_executive_planning_report(business_id)["executivePlanningReport"]
            discovery = orchestrator.generate_opportunity_discovery_report(business_id)["opportunityDiscoveryReport"]
            optimization = orchestrator.generate_execution_optimization_report(business_id)["executionOptimizationReport"]
            enterprise = orchestrator.create_enterprise_organization("Genesis Enterprise")["enterpriseOrganization"]

            self.assertFalse(validate_organizational_intelligence_report_payload(organizational))
            self.assertFalse(validate_simulation_report_payload(simulation))
            self.assertFalse(validate_executive_planning_report_payload(planning))
            self.assertFalse(validate_opportunity_discovery_report_payload(discovery))
            self.assertFalse(validate_execution_optimization_report_payload(optimization))
            self.assertFalse(validate_enterprise_organization_payload(enterprise))
            self.assertTrue(organizational["organizationalMemory"]["initialized"])
            self.assertTrue(organizational["knowledgeReuse"]["founderOverrideSupported"])
            self.assertTrue(simulation["pricingSimulation"]["multipleScenariosSupported"])
            self.assertTrue(simulation["executiveRecommendation"]["bestScenarioSelected"])
            self.assertTrue(simulation["simulationLearning"]["modelsImprovedUsingOrganizationalKnowledge"])
            self.assertTrue(planning["annualBusinessPlan"]["generated"])
            self.assertTrue(planning["initiativePrioritization"]["ranked"])
            self.assertTrue(planning["executiveReview"]["decisionRegisterUpdated"])
            self.assertTrue(discovery["opportunityPipeline"]["created"])
            self.assertTrue(discovery["executiveOpportunityReport"]["linkedToBusinessMemory"])
            self.assertTrue(optimization["workflowOptimization"]["bottlenecksDetected"])
            self.assertTrue(optimization["adaptiveGovernanceBoundary"]["governanceRulesProtected"])
            self.assertTrue(enterprise["organization"]["multipleBusinessUnitsSupported"])
            self.assertTrue(enterprise["securityAccessControl"]["leastPrivilegeEnforcement"])
            self.assertEqual(store.get_organizational_intelligence_report(business_id)["businessId"], business_id)
            self.assertEqual(store.get_v2_simulation_report(business_id)["businessId"], business_id)
            self.assertEqual(store.get_executive_planning_report(business_id)["businessId"], business_id)
            self.assertEqual(store.get_opportunity_discovery_report(business_id)["businessId"], business_id)
            self.assertEqual(store.get_execution_optimization_report(business_id)["businessId"], business_id)
            self.assertEqual(store.get_enterprise_organization(enterprise["organizationId"])["organizationId"], enterprise["organizationId"])
            self.assertTrue(store.get_v2_decision_register(business_id)["decisions"])


if __name__ == "__main__":
    unittest.main()

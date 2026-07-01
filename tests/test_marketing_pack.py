"""Sprint 5 Marketing Pack tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.marketing.employees import MARKETING_EMPLOYEES, run_marketing_employee, validate_marketing_employee_output
from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from scripts.validate_marketing_pack import validate_marketing_pack_payload


class MarketingPackTests(unittest.TestCase):
    def _creative_flow(self, orchestrator: GenesisOrchestrator) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
        research = orchestrator.submit_idea(
            "Build a premium educational wooden toy business for children aged 3-5 in India.",
            country="India",
            budget="300000 INR",
            timeline="45 days",
        )
        product_blueprint = orchestrator.generate_product_blueprint(research["project"]["id"])["blueprint"]
        creative_pack = orchestrator.generate_creative_pack(product_blueprint["productId"])["creativePack"]
        return research, product_blueprint, creative_pack

    def test_marketing_employee_contracts_are_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            research, product_blueprint, creative_pack = self._creative_flow(orchestrator)
            context = {
                "project": research["project"],
                "workflow": {"id": "workflow-test"},
                "productBlueprint": product_blueprint,
                "creativePack": creative_pack,
                "sections": {},
            }

            for employee_id in MARKETING_EMPLOYEES:
                output = run_marketing_employee(employee_id, context)
                self.assertFalse(validate_marketing_employee_output(output))
                context["sections"][output["section"]] = output

    def test_orchestrator_generates_complete_marketing_pack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            _, _, creative_pack = self._creative_flow(orchestrator)

            result = orchestrator.generate_marketing_pack(creative_pack["creativeId"])
            marketing_pack = result["marketingPack"]

            self.assertEqual(result["project"]["status"], "MARKETING_PACK_COMPLETED")
            self.assertEqual(marketing_pack["reportType"], "MARKETING_PACK")
            self.assertFalse(validate_marketing_pack_payload(marketing_pack))
            self.assertEqual(marketing_pack["departmentStatus"], "COMPLETED")
            self.assertEqual(marketing_pack["marketingDirector"]["employeeId"], "EMP-310")
            self.assertEqual(marketing_pack["salesTransition"]["status"], "READY")
            self.assertEqual(store.get_marketing_pack(creative_pack["creativeId"])["marketingId"], creative_pack["creativeId"])
            self.assertTrue(store.get_marketing_strategy_report(creative_pack["creativeId"])["launchPositioning"])
            self.assertTrue(store.get_seo_report(creative_pack["creativeId"])["keywords"])
            self.assertTrue(store.get_social_marketing_report(creative_pack["creativeId"])["instagramCalendar"])
            self.assertTrue(store.get_ads_report(creative_pack["creativeId"])["metaAds"])
            self.assertTrue(store.get_listing_report(creative_pack["creativeId"])["title"])
            self.assertTrue(store.get_launch_report(creative_pack["creativeId"]))

    def test_founder_acceptance_wooden_toy_marketing_pack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            _, _, creative_pack = self._creative_flow(orchestrator)
            marketing_pack = orchestrator.generate_marketing_pack(creative_pack["creativeId"])["marketingPack"]

            self.assertIn("launchPositioning", marketing_pack)
            self.assertTrue(marketing_pack["goToMarketStrategy"])
            self.assertTrue(marketing_pack["launchRoadmap"])
            self.assertTrue(marketing_pack["marketingBudget"])
            self.assertTrue(marketing_pack["channelPrioritization"])
            self.assertTrue(marketing_pack["customerAcquisitionStrategy"])
            self.assertTrue(marketing_pack["contentStrategy"]["contentPillars"])
            self.assertTrue(marketing_pack["marketingCalendar"]["dailyPosts"])
            self.assertTrue(marketing_pack["marketingContent"]["instagramCaptions"])
            self.assertTrue(marketing_pack["advertisingStrategy"]["campaignObjectives"])
            self.assertTrue(marketing_pack["retentionStrategy"])
            self.assertTrue(marketing_pack["referralStrategy"])
            self.assertTrue(marketing_pack["seoPlan"]["keywords"])
            self.assertTrue(marketing_pack["socialMediaPlan"]["instagramCalendar"])
            self.assertTrue(marketing_pack["socialMediaPlan"]["facebookCalendar"])
            self.assertTrue(marketing_pack["socialMediaPlan"]["youtubeContentPlan"])
            self.assertTrue(marketing_pack["socialMediaPlan"]["reelScripts"])
            self.assertTrue(marketing_pack["advertisingPlan"]["metaAds"])
            self.assertTrue(marketing_pack["advertisingPlan"]["googleAds"])
            self.assertTrue(marketing_pack["advertisingPlan"]["amazonAdsStrategy"])
            self.assertTrue(marketing_pack["advertisingPlan"]["abTestMatrix"])
            self.assertTrue(marketing_pack["landingPageCopy"]["hero"])
            self.assertTrue(marketing_pack["marketplaceListing"]["title"])
            self.assertTrue(marketing_pack["ecommerceDeliverables"]["shopifyProductPage"])
            self.assertTrue(marketing_pack["crmDeliverables"]["cartAbandonmentEmails"])
            self.assertTrue(marketing_pack["salesFunnel"]["funnelArchitecture"])
            self.assertTrue(marketing_pack["salesFunnel"]["customerTouchpoints"])
            self.assertTrue(marketing_pack["salesFunnel"]["conversionGoals"])
            self.assertTrue(marketing_pack["emailCampaign"]["sequence"])
            self.assertTrue(marketing_pack["whatsappCampaign"]["broadcasts"])
            self.assertTrue(marketing_pack["influencerStrategy"]["creatorProfiles"])
            self.assertTrue(marketing_pack["analyticsPlan"]["kpiDashboard"])
            self.assertTrue(marketing_pack["analyticsPlan"]["cac"])
            self.assertTrue(marketing_pack["analyticsPlan"]["roas"])
            self.assertTrue(marketing_pack["analyticsPlan"]["ctr"])
            self.assertTrue(marketing_pack["analyticsPlan"]["conversionRate"])
            self.assertTrue(marketing_pack["analyticsPlan"]["aov"])
            self.assertTrue(marketing_pack["analyticsPlan"]["ltv"])
            self.assertTrue(marketing_pack["aiDeliverables"]["automationWorkflows"])
            self.assertGreaterEqual(marketing_pack["launchReadinessScore"]["score"], 0)
            self.assertLessEqual(marketing_pack["launchReadinessScore"]["score"], 100)
            self.assertTrue(marketing_pack["launchPlan"])
            self.assertTrue(marketing_pack["marketingLaunchKit"]["downloadable"])
            self.assertEqual(marketing_pack["validationReport"]["status"], "PASS")
            self.assertTrue(marketing_pack["knowledgeBaseEntries"])
            self.assertTrue(marketing_pack["campaignQaReport"]["checks"])
            self.assertTrue(marketing_pack["founderApprovalChecklist"])


if __name__ == "__main__":
    unittest.main()

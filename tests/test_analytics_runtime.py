"""Sprint 7 analytics and continuous monitoring tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from scripts.validate_business_intelligence_report import validate_business_intelligence_report_payload


class AnalyticsRuntimeTests(unittest.TestCase):
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
        launch_package = orchestrator.generate_business_launch_package(marketing_pack["marketingId"])["businessLaunchPackage"]
        return orchestrator.generate_business_operating_plan(launch_package["launchId"])["businessOperatingPlan"]["businessId"]

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

    def test_business_intelligence_report_covers_sprint7_stories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            launch_package = self._launch_flow(orchestrator)

            result = orchestrator.generate_business_intelligence_report(launch_package["launchId"])
            report = result["businessIntelligenceReport"]

            self.assertEqual(result["project"]["status"], "BUSINESS_INTELLIGENCE_COMPLETED")
            self.assertEqual(report["reportType"], "BUSINESS_INTELLIGENCE_REPORT")
            self.assertFalse(validate_business_intelligence_report_payload(report))
            self.assertTrue(report["businessIntelligenceDepartment"]["initialized"])
            self.assertTrue(report["chiefBusinessAnalyst"])
            self.assertTrue(report["metricsCollection"]["collected"])
            self.assertTrue(report["salesAnalytics"]["reportsStored"])
            self.assertTrue(report["marketingAnalytics"]["bestPerformingChannels"])
            self.assertTrue(report["customerAnalytics"]["customerSegments"])
            self.assertTrue(report["productPerformanceAnalytics"]["productRankingGenerated"])
            self.assertGreaterEqual(report["businessHealth"]["score"], 0)
            self.assertTrue(report["recommendations"])
            self.assertTrue(report["executiveBusinessReport"]["downloadable"])
            self.assertEqual(report["workflowTransition"], "BUSINESS_OPERATING_SYSTEM")
            self.assertEqual(store.get_business_intelligence_report(report["businessId"])["businessId"], report["businessId"])

    def test_metrics_ingestion_refreshes_dashboard_alerts_and_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            business_id = self._businessos_flow(orchestrator)

            result = orchestrator.ingest_business_metrics(
                business_id,
                {
                    "revenue": 60000,
                    "orders": 50,
                    "adSpend": 40000,
                    "clicks": 1200,
                    "impressions": 60000,
                    "inventoryOnHand": 12,
                    "rating": 4.1,
                    "reviews": 18,
                    "cash": 125000,
                    "grossProfit": 33000,
                },
                source="test",
            )

            dashboard = result["dashboard"]
            self.assertEqual(dashboard["reportType"], "BUSINESS_DASHBOARD")
            self.assertEqual(dashboard["metricEventCount"], 1)
            self.assertGreater(dashboard["derivedMetrics"]["roas"], 0)
            self.assertTrue(result["alerts"])
            self.assertTrue(any(alert["type"] == "inventory.low" for alert in result["alerts"]))
            self.assertTrue(result["recommendations"])
            self.assertTrue(result["knowledgeEntry"]["lessons"])
            self.assertEqual(store.get_business_dashboard(business_id)["businessId"], business_id)
            self.assertTrue(store.get_business_alerts(business_id)["alerts"])
            self.assertEqual(len(store.list_business_metric_events(business_id)), 1)
            self.assertGreaterEqual(len(store.list_business_knowledge(business_id)), 1)

    def test_revenue_drop_generates_alert_against_previous_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            business_id = self._businessos_flow(orchestrator)

            orchestrator.ingest_business_metrics(business_id, {"revenue": 100000, "orders": 70, "inventoryOnHand": 80, "cash": 200000}, source="day-1", observed_at="2026-06-29T09:00:00Z")
            result = orchestrator.ingest_business_metrics(business_id, {"revenue": 50000, "orders": 32, "inventoryOnHand": 70, "cash": 190000}, source="day-2", observed_at="2026-06-30T09:00:00Z")

            self.assertTrue(any(alert["type"] == "revenue.drop" for alert in result["alerts"]))


if __name__ == "__main__":
    unittest.main()

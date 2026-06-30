"""Sprint 7 analytics and continuous monitoring tests."""

from __future__ import annotations

import tempfile
import unittest

from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore


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
            self.assertEqual(len(store.list_business_knowledge(business_id)), 1)

    def test_revenue_drop_generates_alert_against_previous_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            business_id = self._businessos_flow(orchestrator)

            orchestrator.ingest_business_metrics(business_id, {"revenue": 100000, "orders": 70, "inventoryOnHand": 80, "cash": 200000}, source="day-1", observed_at="2026-06-29T09:00:00Z")
            result = orchestrator.ingest_business_metrics(business_id, {"revenue": 50000, "orders": 32, "inventoryOnHand": 70, "cash": 190000}, source="day-2", observed_at="2026-06-30T09:00:00Z")

            self.assertTrue(any(alert["type"] == "revenue.drop" for alert in result["alerts"]))


if __name__ == "__main__":
    unittest.main()

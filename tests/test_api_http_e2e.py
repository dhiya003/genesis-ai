"""HTTP-level API e2e test for Sprint 2 research flow."""

from __future__ import annotations

import json
import tempfile
from threading import Thread
import unittest
from urllib import request

from apps.api.app import create_server
from config import RuntimeConfig


class ApiHttpE2ETests(unittest.TestCase):
    def test_http_submit_project_then_retrieve_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = RuntimeConfig(api_host="127.0.0.1", api_port=0, data_dir=directory, environment="test")
            server = create_server(config)
            host, port = server.server_address
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                payload = json.dumps({"idea": "Create a coffee lovers product brand for India."}).encode("utf-8")
                submit_request = request.Request(
                    f"http://{host}:{port}/projects",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(submit_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    submitted = json.loads(response.read().decode("utf-8"))

                project_id = submitted["project"]["id"]
                with request.urlopen(f"http://{host}:{port}/reports/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    report = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/projects/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    project_payload = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/version", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    version = json.loads(response.read().decode("utf-8"))

                product_request = request.Request(
                    f"http://{host}:{port}/projects/{project_id}/product-definition",
                    data=json.dumps({}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(product_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    product_run = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/product-definitions/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_definition = json.loads(response.read().decode("utf-8"))

                blueprint_request = request.Request(
                    f"http://{host}:{port}/products/generate",
                    data=json.dumps({"projectId": project_id}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(blueprint_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    blueprint_run = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/products/{project_id}/blueprint", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_blueprint = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/products/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_bundle = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/products/{project_id}/bom", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_bom = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/products/{project_id}/cost", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_cost = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/products/{project_id}/suppliers", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_suppliers = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/products/{project_id}/packaging", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_packaging = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/products/{project_id}/profitability", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    product_profitability = json.loads(response.read().decode("utf-8"))

                creative_request = request.Request(
                    f"http://{host}:{port}/creative/generate",
                    data=json.dumps({"productId": project_id}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(creative_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    creative_run = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/creative/{project_id}/pack", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    creative_pack = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/creative/{project_id}/brand", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    creative_brand = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/creative/{project_id}/assets", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    creative_assets = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/brand/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    brand_alias = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/packaging/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    packaging_alias = json.loads(response.read().decode("utf-8"))

                marketing_request = request.Request(
                    f"http://{host}:{port}/marketing/generate",
                    data=json.dumps({"creativeId": project_id}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(marketing_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    marketing_run = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/marketing/{project_id}/pack", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    marketing_pack = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/marketing/{project_id}/seo", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    marketing_seo = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/campaigns/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    campaigns_alias = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/content-calendar/{project_id}", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    calendar_alias = json.loads(response.read().decode("utf-8"))

                launch_request = request.Request(
                    f"http://{host}:{port}/launch/generate",
                    data=json.dumps({"marketingId": project_id}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(launch_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    launch_run = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/launch/{project_id}/package", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    launch_package = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/launch/{project_id}/status", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    launch_status = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/launch/{project_id}/assets", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    launch_assets = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/launch/{project_id}/report", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    launch_report = json.loads(response.read().decode("utf-8"))

                businessos_request = request.Request(
                    f"http://{host}:{port}/businessos/generate",
                    data=json.dumps({"launchId": project_id}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(businessos_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    businessos_run = json.loads(response.read().decode("utf-8"))

                with request.urlopen(f"http://{host}:{port}/businessos/{project_id}/plan", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    businessos_plan = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/businessos/{project_id}/digital-twin", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    digital_twin = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/businessos/{project_id}/health", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    business_health = json.loads(response.read().decode("utf-8"))
                with request.urlopen(f"http://{host}:{port}/businessos/{project_id}/recommendations", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    recommendations = json.loads(response.read().decode("utf-8"))

                self.assertEqual(report["reportType"], "RESEARCH_REPORT")
                self.assertEqual(report["projectId"], project_id)
                self.assertIn("executiveSummary", report)
                self.assertIn("opportunityScore", report)
                self.assertIn("citations", report)
                self.assertEqual(project_payload["project"]["id"], project_id)
                self.assertTrue(project_payload["tasks"])
                self.assertTrue(project_payload["deliverables"])
                self.assertTrue(project_payload["auditLogs"])
                self.assertEqual(version["version"], "1.0.0-foundation")
                self.assertEqual(product_run["productDefinition"]["reportType"], "PRODUCT_DEFINITION")
                self.assertEqual(product_definition["reportType"], "PRODUCT_DEFINITION")
                self.assertEqual(product_definition["projectId"], project_id)
                self.assertIn("variantMatrix", product_definition)
                self.assertEqual(blueprint_run["blueprint"]["reportType"], "PRODUCT_BLUEPRINT")
                self.assertEqual(product_blueprint["reportType"], "PRODUCT_BLUEPRINT")
                self.assertEqual(product_bundle["blueprint"]["reportType"], "PRODUCT_BLUEPRINT")
                self.assertTrue(product_bom["items"])
                self.assertGreater(product_cost["landedCost"], 0)
                self.assertTrue(product_suppliers["shortlist"])
                self.assertTrue(product_packaging["packagingDimensions"])
                self.assertGreater(product_profitability["profitPerUnit"], 0)
                self.assertEqual(creative_run["creativePack"]["reportType"], "CREATIVE_PACK")
                self.assertEqual(creative_pack["reportType"], "CREATIVE_PACK")
                self.assertTrue(creative_brand["brandName"])
                self.assertTrue(creative_assets["assets"])
                self.assertGreaterEqual(creative_assets["summary"]["png"], 1)
                self.assertEqual(brand_alias["brandName"], creative_brand["brandName"])
                self.assertTrue(packaging_alias["panelContent"])
                self.assertEqual(marketing_run["marketingPack"]["reportType"], "MARKETING_PACK")
                self.assertEqual(marketing_pack["reportType"], "MARKETING_PACK")
                self.assertTrue(marketing_seo["keywords"])
                self.assertTrue(campaigns_alias["advertisingPlan"]["metaAds"])
                self.assertTrue(calendar_alias["instagramCalendar"])
                self.assertEqual(launch_run["businessLaunchPackage"]["reportType"], "BUSINESS_LAUNCH_PACKAGE")
                self.assertEqual(launch_package["reportType"], "BUSINESS_LAUNCH_PACKAGE")
                self.assertIn(launch_status["status"], {"READY_FOR_FOUNDER_APPROVAL", "NEEDS_REVIEW"})
                self.assertTrue(launch_assets["assets"])
                self.assertTrue(launch_report["channelsPrepared"])
                self.assertEqual(businessos_run["businessOperatingPlan"]["reportType"], "BUSINESS_OPERATING_PLAN")
                self.assertEqual(businessos_plan["reportType"], "BUSINESS_OPERATING_PLAN")
                self.assertTrue(digital_twin["products"])
                self.assertGreaterEqual(business_health["overallBusinessHealthScore"], 0)
                self.assertTrue(recommendations["recommendations"])
                self.assertIn("trendAnalysis", report)
                self.assertIn("competitorAnalysis", report)
                self.assertIn("customerAnalysis", report)
                self.assertIn("productResearch", report)
                self.assertIn("recommendation", report)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()

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

                self.assertEqual(report["reportType"], "RESEARCH_REPORT")
                self.assertEqual(report["projectId"], project_id)
                self.assertIn("executiveSummary", report)
                self.assertIn("opportunityScore", report)
                self.assertIn("citations", report)
                self.assertEqual(project_payload["project"]["id"], project_id)
                self.assertTrue(project_payload["tasks"])
                self.assertTrue(project_payload["deliverables"])
                self.assertTrue(project_payload["auditLogs"])
                self.assertEqual(version["version"], "0.3.0")
                self.assertEqual(product_run["productDefinition"]["reportType"], "PRODUCT_DEFINITION")
                self.assertEqual(product_definition["reportType"], "PRODUCT_DEFINITION")
                self.assertEqual(product_definition["projectId"], project_id)
                self.assertIn("variantMatrix", product_definition)
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

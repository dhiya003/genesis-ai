"""Production guardrail tests for auth, integrations, and dashboard UI."""

from __future__ import annotations

import json
import tempfile
from threading import Thread
import unittest
from urllib import error, request

from apps.api.app import create_server
from apps.integrations.registry import integration_status
from config import RuntimeConfig


class ProductionGuardrailTests(unittest.TestCase):
    def test_api_key_rbac_and_tenant_guardrails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = RuntimeConfig(
                api_host="127.0.0.1",
                api_port=0,
                data_dir=directory,
                environment="test",
                auth_mode="api_key",
                api_keys="founder=founder-key,viewer=viewer-key",
                tenant_id="tenant-a",
                require_tenant_header=True,
            )
            server = create_server(config)
            host, port = server.server_address
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                body = json.dumps({"idea": "Create a coffee lovers product brand for India."}).encode("utf-8")
                missing_auth = request.Request(f"http://{host}:{port}/projects", data=body, headers={"Content-Type": "application/json"}, method="POST")
                with self.assertRaises(error.HTTPError) as missing_error:
                    request.urlopen(missing_auth, timeout=10)
                self.assertEqual(missing_error.exception.code, 401)

                viewer_request = request.Request(
                    f"http://{host}:{port}/projects",
                    data=body,
                    headers={"Content-Type": "application/json", "Authorization": "Bearer viewer-key", "X-Genesis-Tenant-ID": "tenant-a"},
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as viewer_error:
                    request.urlopen(viewer_request, timeout=10)
                self.assertEqual(viewer_error.exception.code, 403)

                wrong_tenant = request.Request(
                    f"http://{host}:{port}/projects",
                    data=body,
                    headers={"Content-Type": "application/json", "Authorization": "Bearer founder-key", "X-Genesis-Tenant-ID": "tenant-b"},
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as tenant_error:
                    request.urlopen(wrong_tenant, timeout=10)
                self.assertEqual(tenant_error.exception.code, 403)

                founder_request = request.Request(
                    f"http://{host}:{port}/projects",
                    data=body,
                    headers={"Content-Type": "application/json", "Authorization": "Bearer founder-key", "X-Genesis-Tenant-ID": "tenant-a"},
                    method="POST",
                )
                with request.urlopen(founder_request, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    submitted = json.loads(response.read().decode("utf-8"))

                project_id = submitted["project"]["id"]
                viewer_get = request.Request(
                    f"http://{host}:{port}/reports/{project_id}",
                    headers={"Authorization": "Bearer viewer-key", "X-Genesis-Tenant-ID": "tenant-a"},
                    method="GET",
                )
                with request.urlopen(viewer_get, timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    report = json.loads(response.read().decode("utf-8"))
                self.assertEqual(report["reportType"], "RESEARCH_REPORT")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_businessos_dashboard_html_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = RuntimeConfig(api_host="127.0.0.1", api_port=0, data_dir=directory, environment="test")
            server = create_server(config)
            server.store.save_business_dashboard(  # type: ignore[attr-defined]
                "biz-1",
                {
                    "reportType": "BUSINESS_DASHBOARD",
                    "businessId": "biz-1",
                    "generatedAt": "2026-06-30T00:00:00Z",
                    "currentState": "LIVE_METRICS_INGESTED",
                    "latestMetrics": {"revenue": 75000, "orders": 50, "inventoryOnHand": 12, "cash": 100000},
                    "derivedMetrics": {"roas": 1.1},
                    "businessHealth": {"overallBusinessHealthScore": 68, "status": "WATCH"},
                    "departmentDashboards": [{"department": "Sales", "score": 70, "kpis": {"revenue": 75000}}],
                },
            )
            server.store.save_business_alerts("biz-1", {"businessId": "biz-1", "alerts": [{"severity": "HIGH", "type": "inventory.low", "message": "Inventory low", "recommendedAction": "Reorder"}]})  # type: ignore[attr-defined]
            server.store.save_business_knowledge_entry({"id": "k1", "businessId": "biz-1", "createdAt": "2026-06-30T00:00:00Z", "type": "METRIC_INGESTION", "lessons": ["Reorder inventory"]})  # type: ignore[attr-defined]
            host, port = server.server_address
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with request.urlopen(f"http://{host}:{port}/dashboard/businessos/biz-1", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn("text/html", response.headers["Content-Type"])
                    html = response.read().decode("utf-8")
                self.assertIn("Genesis BusinessOS Dashboard", html)
                self.assertIn("inventory.low", html)
                self.assertIn("Department Health", html)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_integration_status_is_sanitized(self) -> None:
        status = integration_status({"OPENAI_API_KEY": "secret-value", "SERPAPI_API_KEY": "serp-secret"})
        self.assertEqual(status["reportType"], "INTEGRATION_READINESS")
        providers = {provider["name"]: provider for provider in status["providers"]}  # type: ignore[index]
        self.assertEqual(providers["openai"]["status"], "READY")
        self.assertEqual(providers["serpapi"]["status"], "READY")
        rendered = json.dumps(status)
        self.assertNotIn("secret-value", rendered)
        self.assertNotIn("serp-secret", rendered)


if __name__ == "__main__":
    unittest.main()

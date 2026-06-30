"""Regression tests for Sprint 2.1.1.001 runtime bootstrap."""

from __future__ import annotations

import json
import unittest
from io import StringIO
from unittest.mock import patch

from apps.cli.main import health, main as cli_main
from apps.worker.main import worker_health
from config import RuntimeConfig, load_runtime_config


class RuntimeBootstrapTests(unittest.TestCase):
    def test_runtime_config_uses_safe_defaults(self) -> None:
        config = load_runtime_config({})
        self.assertEqual(config.environment, "development")
        self.assertEqual(config.api_host, "127.0.0.1")
        self.assertEqual(config.api_port, 8000)
        self.assertEqual(config.base_url, "http://127.0.0.1:8000")
        self.assertEqual(config.auth_mode, "off")
        self.assertFalse(config.require_tenant_header)

    def test_runtime_config_loads_production_guardrails(self) -> None:
        config = load_runtime_config(
            {
                "GENESIS_AUTH_MODE": "api_key",
                "GENESIS_API_KEYS": "founder=local-founder-key",
                "GENESIS_TENANT_ID": "tenant-a",
                "GENESIS_REQUIRE_TENANT_HEADER": "true",
            }
        )
        self.assertEqual(config.auth_mode, "api_key")
        self.assertEqual(config.api_keys, "founder=local-founder-key")
        self.assertEqual(config.tenant_id, "tenant-a")
        self.assertTrue(config.require_tenant_header)

    def test_runtime_config_validates_port(self) -> None:
        with self.assertRaises(ValueError):
            load_runtime_config({"GENESIS_API_PORT": "not-a-port"})

    def test_worker_health_contains_queue(self) -> None:
        payload = worker_health(RuntimeConfig(worker_queue_name="test-queue"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["component"], "worker")
        self.assertEqual(payload["queue"], "test-queue")

    def test_cli_health_payload_contains_api_and_worker(self) -> None:
        payload = health(RuntimeConfig(environment="test"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["api"]["environment"], "test")
        self.assertEqual(payload["worker"]["component"], "worker")

    def test_cli_health_command_prints_json(self) -> None:
        output = StringIO()
        with patch("sys.stdout", output):
            exit_code = cli_main(["health"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["api"]["component"], "api")


if __name__ == "__main__":
    unittest.main()

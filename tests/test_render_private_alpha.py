"""Render private-alpha deployment contract tests."""

from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RenderPrivateAlphaTests(unittest.TestCase):
    def test_render_blueprint_enables_private_alpha_guardrails(self) -> None:
        blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")

        self.assertIn("genesis-ai-private-alpha", blueprint)
        self.assertIn("runtime: docker", blueprint)
        self.assertIn("healthCheckPath: /health", blueprint)
        self.assertIn("GENESIS_AUTH_MODE", blueprint)
        self.assertIn("api_key", blueprint)
        self.assertIn("GENESIS_REQUIRE_TENANT_HEADER", blueprint)
        self.assertIn("GENESIS_RESEARCH_PROVIDER", blueprint)
        self.assertIn("deterministic", blueprint)
        self.assertIn("sync: false", blueprint)

    def test_render_runbook_documents_secret_and_durability_limits(self) -> None:
        runbook = (ROOT / "docs/render-private-alpha.md").read_text(encoding="utf-8")

        self.assertIn("Do not commit API keys", runbook)
        self.assertIn("Rotate any key that was pasted into chat", runbook)
        self.assertIn("free Render plan as non-durable", runbook)
        self.assertIn("GENESIS_API_KEYS", runbook)


if __name__ == "__main__":
    unittest.main()

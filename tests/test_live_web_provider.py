"""Tests for live web research provider behavior without network calls."""

from __future__ import annotations

import unittest

from apps.research.providers import LiveWebResearchProvider, WebSearchResult


class FakeSearchClient:
    def search(self, query: str, limit: int = 5) -> list[WebSearchResult]:
        return [
            WebSearchResult(
                title="Coffee gift products India",
                url="https://example.com/coffee-gifts",
                snippet="Coffee gift boxes and accessories are visible in Indian ecommerce search results.",
            ),
            WebSearchResult(
                title="Coffee lovers merchandise",
                url="https://example.com/coffee-merch",
                snippet="Coffee lovers buy mugs, stickers, posters and desk accessories.",
            ),
        ]


class LiveWebResearchProviderTests(unittest.TestCase):
    def test_live_provider_returns_evidence_for_each_employee(self) -> None:
        provider = LiveWebResearchProvider(search_client=FakeSearchClient())
        for employee_id in ["EMP-001", "EMP-002", "EMP-003", "EMP-004"]:
            output = provider.run(employee_id, "Create a coffee lovers product brand for India")
            self.assertEqual(output["evidenceLevel"], "live_web_search")
            self.assertIn("evidence", output)
            self.assertGreaterEqual(len(output["evidence"]), 1)
            self.assertIn("score", output)
            self.assertGreaterEqual(output["score"], 0)
            self.assertLessEqual(output["score"], 100)


if __name__ == "__main__":
    unittest.main()

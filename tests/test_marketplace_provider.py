"""Tests for marketplace-specific live intelligence provider."""

from __future__ import annotations

import unittest

from apps.research.marketplaces import MarketplaceResearchProvider, SearchBackedMarketplaceClient
from apps.research.providers import WebSearchResult


class FakeSearchClient:
    def search(self, query: str, limit: int = 5) -> list[WebSearchResult]:
        return [
            WebSearchResult(title=f"Result for {query}", url="https://example.com/a", snippet="Evidence snippet A"),
            WebSearchResult(title=f"Second result for {query}", url="https://example.com/b", snippet="Evidence snippet B"),
        ][:limit]


class MarketplaceResearchProviderTests(unittest.TestCase):
    def test_marketplace_provider_collects_source_targeted_evidence(self) -> None:
        client = SearchBackedMarketplaceClient(search_client=FakeSearchClient(), per_source_limit=2)
        provider = MarketplaceResearchProvider(client=client)

        for employee_id in ["EMP-001", "EMP-002", "EMP-003", "EMP-004"]:
            output = provider.run(employee_id, "coffee lovers product brand India")
            self.assertEqual(output["evidenceLevel"], "live_marketplace_search")
            self.assertGreaterEqual(len(output["evidence"]), 3)
            self.assertIn("score", output)
            self.assertGreaterEqual(output["score"], 0)
            self.assertLessEqual(output["score"], 100)
            for item in output["evidence"]:
                self.assertIn("source", item)
                self.assertIn("query", item)
                self.assertIn("title", item)
                self.assertIn("url", item)


if __name__ == "__main__":
    unittest.main()

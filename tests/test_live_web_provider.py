"""Tests for live web research provider behavior without network calls."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from apps.research.providers import LiveWebResearchProvider, SerpApiSearchClient, get_web_search_client, WebSearchResult


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

    def test_serpapi_client_parses_organic_results(self) -> None:
        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps(
                    {
                        "organic_results": [
                            {"title": "Wooden toys India", "link": "https://example.com/toys", "snippet": "Premium wooden educational toys."},
                            {"title": "Learning toys", "link": "https://example.com/learning", "snippet": "Activity kits for preschool children."},
                        ]
                    }
                ).encode("utf-8")

        with patch("apps.research.providers.request.urlopen", return_value=FakeResponse()) as urlopen:
            results = SerpApiSearchClient(api_key="test-key").search("wooden toy India", limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Wooden toys India")
        requested_url = urlopen.call_args.args[0].full_url
        self.assertIn("serpapi.com/search.json", requested_url)
        self.assertIn("engine=google", requested_url)

    def test_search_client_uses_serpapi_when_key_is_configured(self) -> None:
        with patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}, clear=False):
            self.assertIsInstance(get_web_search_client(), SerpApiSearchClient)


if __name__ == "__main__":
    unittest.main()

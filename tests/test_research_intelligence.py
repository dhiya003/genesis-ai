"""Tests for Sprint 2 research intelligence utilities."""

from __future__ import annotations

import unittest

from apps.research.intelligence import CitationEngine, ConfidenceEngine, SearchManager, collect_parallel
from apps.research.providers import WebSearchResult


class FakeSearchClient:
    def __init__(self) -> None:
        self.calls = 0

    def search(self, query: str, limit: int = 5) -> list[WebSearchResult]:
        self.calls += 1
        return [WebSearchResult(title="A", url="https://example.com/a", snippet="Snippet")]


class ResearchIntelligenceTests(unittest.TestCase):
    def test_search_manager_caches_queries(self) -> None:
        client = FakeSearchClient()
        manager = SearchManager(client=client)
        first = manager.search("coffee", limit=2)
        second = manager.search("coffee", limit=2)
        self.assertEqual(first, second)
        self.assertEqual(client.calls, 1)
        self.assertEqual(manager.usage.cache_hits, 1)

    def test_confidence_engine_scores_evidence(self) -> None:
        confidence = ConfidenceEngine().score([
            {"source": "amazon", "url": "https://amazon.in/a", "snippet": "Review"},
            {"source": "instagram", "url": "https://instagram.com/a", "snippet": "Post"},
        ])
        self.assertIn(confidence["level"], {"LOW", "MEDIUM", "HIGH"})
        self.assertGreater(confidence["score"], 0)

    def test_citation_engine_deduplicates_urls(self) -> None:
        citations = CitationEngine().build([
            {"title": "A", "url": "https://example.com/a", "snippet": "One"},
            {"title": "A duplicate", "url": "https://example.com/a", "snippet": "Two"},
        ])
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["url"], "https://example.com/a")

    def test_collect_parallel_runs_all_employees(self) -> None:
        outputs = collect_parallel(["EMP-001", "EMP-002"], lambda employee_id: {"employeeId": employee_id})
        self.assertEqual({item["employeeId"] for item in outputs}, {"EMP-001", "EMP-002"})


if __name__ == "__main__":
    unittest.main()

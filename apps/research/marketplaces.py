"""Marketplace and social-source research adapters for Genesis Sprint 2.

These adapters provide marketplace-specific live intelligence without requiring
paid API credentials. They use the existing web-search boundary with targeted
site queries. This is not a replacement for official Amazon/Meta/Shopify APIs;
it is the Sprint 2 live intelligence bridge until governed API connectors are
added.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from apps.research.providers import WebSearchClient, WebSearchResult


@dataclass(frozen=True)
class SourceQuery:
    """One targeted live intelligence query."""

    source: str
    query: str
    intent: str


class MarketplaceIntelligenceClient(Protocol):
    """Marketplace/social intelligence boundary."""

    def collect(self, idea: str, employee_id: str) -> list[dict[str, Any]]:
        """Return normalized source evidence for one employee."""


@dataclass(frozen=True)
class SearchBackedMarketplaceClient:
    """Collect live marketplace evidence using source-specific search queries."""

    search_client: WebSearchClient
    per_source_limit: int = 3

    def collect(self, idea: str, employee_id: str) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []
        for source_query in _queries_for_employee(idea, employee_id):
            results = self.search_client.search(source_query.query, limit=self.per_source_limit)
            evidence.extend(_normalize_results(source_query, results))
        return evidence


@dataclass(frozen=True)
class MarketplaceResearchProvider:
    """Live source-targeted provider for market, marketplace, and social evidence."""

    client: MarketplaceIntelligenceClient

    def run(self, employee_id: str, idea: str) -> dict[str, Any]:
        evidence = self.client.collect(idea, employee_id)
        score = _score_marketplace_evidence(evidence)
        if employee_id == "EMP-001":
            return {
                "section": "trendAnalysis",
                "score": score,
                "summary": _summary("trend and demand", idea, evidence),
                "signals": _snippets(evidence),
                "evidence": evidence,
                "evidenceLevel": "live_marketplace_search",
            }
        if employee_id == "EMP-002":
            return {
                "section": "competitorAnalysis",
                "score": max(45, 95 - score // 4),
                "summary": _summary("competitor and pricing", idea, evidence),
                "competitorTypes": _titles(evidence),
                "differentiation": [
                    "Avoid direct imitation of marketplace or social listings.",
                    "Compare bundles, price anchors, reviews, shipping promises, and presentation quality.",
                    "Use competitor density to decide whether to niche down before production.",
                ],
                "evidence": evidence,
                "evidenceLevel": "live_marketplace_search",
            }
        if employee_id == "EMP-003":
            return {
                "section": "customerAnalysis",
                "score": score,
                "summary": _summary("customer demand", idea, evidence),
                "segments": [
                    "Marketplace buyers comparing current offers",
                    "Instagram/Facebook shoppers responding to visual positioning",
                    "Niche customers visible through reviews, captions, and product pages",
                ],
                "objections": [
                    "Search evidence does not prove conversion; validate with real conversations.",
                    "Price, trust, shipping, and product uniqueness remain the biggest blockers.",
                ],
                "evidence": evidence,
                "evidenceLevel": "live_marketplace_search",
            }
        if employee_id == "EMP-004":
            return {
                "section": "productResearch",
                "score": score,
                "summary": _summary("product opportunity", idea, evidence),
                "recommendedProducts": _product_candidates(idea, evidence),
                "mvpRecommendation": "Choose the lightest, easiest-to-ship product visible in marketplace evidence and validate it manually before inventory spend.",
                "evidence": evidence,
                "evidenceLevel": "live_marketplace_search",
            }
        raise ValueError(f"Unknown research employee: {employee_id}")


def _queries_for_employee(idea: str, employee_id: str) -> list[SourceQuery]:
    common = _clean_idea(idea)
    if employee_id == "EMP-001":
        return [
            SourceQuery("amazon_in", f"site:amazon.in {common} bestseller India", "trend"),
            SourceQuery("google_shopping", f"{common} buy online India price", "trend"),
            SourceQuery("instagram", f"site:instagram.com {common} India", "social_trend"),
        ]
    if employee_id == "EMP-002":
        return [
            SourceQuery("amazon_in", f"site:amazon.in {common} price reviews", "competitors"),
            SourceQuery("etsy", f"site:etsy.com {common} gift product", "competitors"),
            SourceQuery("instagram", f"site:instagram.com {common} shop India", "competitors"),
        ]
    if employee_id == "EMP-003":
        return [
            SourceQuery("amazon_in", f"site:amazon.in {common} reviews", "customer_reviews"),
            SourceQuery("reddit_quora", f"{common} India reviews customer demand", "customer_voice"),
            SourceQuery("facebook", f"site:facebook.com {common} India", "social_demand"),
        ]
    if employee_id == "EMP-004":
        return [
            SourceQuery("amazon_in", f"site:amazon.in {common} gift set", "product_ideas"),
            SourceQuery("etsy", f"site:etsy.com {common} printable sticker gift", "product_ideas"),
            SourceQuery("shopify_web", f"{common} Shopify India store product", "product_ideas"),
        ]
    raise ValueError(f"Unknown research employee: {employee_id}")


def _normalize_results(source_query: SourceQuery, results: list[WebSearchResult]) -> list[dict[str, Any]]:
    normalized = []
    for result in results:
        normalized.append(
            {
                "source": source_query.source,
                "intent": source_query.intent,
                "query": source_query.query,
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
            }
        )
    return normalized


def _score_marketplace_evidence(evidence: list[dict[str, Any]]) -> int:
    source_count = len({item.get("source") for item in evidence})
    item_count = len(evidence)
    if source_count >= 3 and item_count >= 7:
        return 82
    if source_count >= 2 and item_count >= 4:
        return 72
    if item_count >= 1:
        return 58
    return 35


def _summary(topic: str, idea: str, evidence: list[dict[str, Any]]) -> str:
    if not evidence:
        return f"No marketplace-specific live evidence found for {topic} around '{idea}'. Treat as low confidence."
    sources = ", ".join(sorted({str(item.get("source")) for item in evidence if item.get("source")}))
    top = "; ".join(str(item.get("title")) for item in evidence[:2] if item.get("title"))
    return f"Marketplace-specific live evidence for {topic} around '{idea}' was found across {sources}. Top signals: {top}."


def _titles(evidence: list[dict[str, Any]]) -> list[str]:
    return [str(item["title"]) for item in evidence if item.get("title")][:8]


def _snippets(evidence: list[dict[str, Any]]) -> list[str]:
    snippets = [str(item["snippet"]) for item in evidence if item.get("snippet")]
    return snippets[:8] or _titles(evidence)


def _product_candidates(idea: str, evidence: list[dict[str, Any]]) -> list[str]:
    candidates = [
        f"{idea}: low-cost MVP kit",
        f"{idea}: lightweight giftable accessory",
        f"{idea}: sticker/printable starter pack",
    ]
    return candidates + _titles(evidence)[:4]


def _clean_idea(idea: str) -> str:
    return " ".join(idea.strip().split())

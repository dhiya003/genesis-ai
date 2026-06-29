"""Research intelligence utilities for Sprint 2B.

This module centralizes source aggregation, confidence scoring, citations, and
basic cost/usage accounting. It is intentionally dependency-free so it can run
inside CI and local development without secrets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from time import perf_counter, sleep
from typing import Any, Callable

from apps.research.providers import WebSearchClient, WebSearchResult


@dataclass
class SearchUsage:
    """Usage accounting for one search manager instance."""

    requests: int = 0
    cache_hits: int = 0
    runtime_seconds: float = 0.0

    def as_dict(self) -> dict[str, float | int]:
        return {
            "requests": self.requests,
            "cacheHits": self.cache_hits,
            "runtimeSeconds": round(self.runtime_seconds, 4),
        }


@dataclass
class SearchManager:
    """Aggregates and caches live search requests for a workflow."""

    client: WebSearchClient
    rate_limit_seconds: float = 0.0
    cache: dict[str, list[WebSearchResult]] = field(default_factory=dict)
    usage: SearchUsage = field(default_factory=SearchUsage)
    last_request_at: float | None = None

    def search(self, query: str, limit: int = 5) -> list[WebSearchResult]:
        key = _cache_key(query, limit)
        if key in self.cache:
            self.usage.cache_hits += 1
            return list(self.cache[key])
        self._rate_limit()
        start = perf_counter()
        self.usage.requests += 1
        results = self.client.search(query, limit=limit)
        self.last_request_at = perf_counter()
        self.usage.runtime_seconds += perf_counter() - start
        self.cache[key] = list(results)
        return results

    def search_many(self, queries: list[str], limit: int = 5) -> dict[str, list[WebSearchResult]]:
        unique_queries = list(dict.fromkeys(query.strip() for query in queries if query.strip()))
        return {query: self.search(query, limit=limit) for query in unique_queries}

    def _rate_limit(self) -> None:
        if not self.rate_limit_seconds or self.last_request_at is None:
            return
        elapsed = perf_counter() - self.last_request_at
        remaining = self.rate_limit_seconds - elapsed
        if remaining > 0:
            sleep(remaining)


@dataclass(frozen=True)
class ConfidenceEngine:
    """Calculates evidence confidence from source diversity and completeness."""

    def score(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        if not evidence:
            return {
                "score": 0.2,
                "level": "LOW",
                "reasons": ["No external evidence was collected."],
            }
        sources = {str(item.get("source") or _domain(str(item.get("url", "")))) for item in evidence if item.get("source") or item.get("url")}
        with_url = sum(1 for item in evidence if item.get("url"))
        with_snippet = sum(1 for item in evidence if item.get("snippet"))
        diversity = min(len(sources) / 4, 1.0)
        volume = min(len(evidence) / 10, 1.0)
        completeness = ((with_url + with_snippet) / max(len(evidence) * 2, 1))
        raw = (0.4 * diversity) + (0.35 * volume) + (0.25 * completeness)
        score = round(max(0.0, min(raw, 1.0)), 2)
        if score >= 0.75:
            level = "HIGH"
        elif score >= 0.5:
            level = "MEDIUM"
        else:
            level = "LOW"
        return {
            "score": score,
            "level": level,
            "sourceCount": len(sources),
            "evidenceCount": len(evidence),
            "reasons": [
                f"{len(evidence)} evidence items collected.",
                f"{len(sources)} unique source groups found.",
                f"{with_snippet} items include snippets.",
            ],
        }


@dataclass(frozen=True)
class CitationEngine:
    """Builds source citations from collected research evidence."""

    def build(self, evidence: list[dict[str, Any]], limit: int = 10) -> list[dict[str, str]]:
        citations: list[dict[str, str]] = []
        seen: set[str] = set()
        for item in evidence:
            url = str(item.get("url", "")).strip()
            title = str(item.get("title", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            citations.append(
                {
                    "title": title or url,
                    "url": url,
                    "source": str(item.get("source") or _domain(url)),
                    "snippet": str(item.get("snippet", ""))[:280],
                }
            )
            if len(citations) >= limit:
                break
        return citations


@dataclass
class CostTracker:
    """Tracks provider usage and estimated cost per workflow."""

    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, label: str, usage: dict[str, Any], estimated_cost_inr: float = 0.0) -> None:
        self.events.append({"label": label, "usage": usage, "estimatedCostInr": round(estimated_cost_inr, 4)})

    def summary(self) -> dict[str, Any]:
        return {
            "events": self.events,
            "totalEstimatedCostInr": round(sum(float(item.get("estimatedCostInr", 0.0)) for item in self.events), 4),
        }


def collect_parallel(employee_ids: list[str], run_one: Callable[[str], dict[str, Any]]) -> list[dict[str, Any]]:
    """Run independent employees concurrently using stdlib threads."""

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=max(1, min(len(employee_ids), 4))) as executor:
        return list(executor.map(run_one, employee_ids))


def _cache_key(query: str, limit: int) -> str:
    return sha256(f"{query.strip().lower()}::{limit}".encode("utf-8")).hexdigest()


def _domain(url: str) -> str:
    cleaned = url.replace("https://", "").replace("http://", "")
    return cleaned.split("/", 1)[0] if cleaned else "unknown"

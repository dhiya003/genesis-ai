"""Research execution providers for Genesis employees.

Sprint 2 supports three provider modes:

- deterministic: credential-free local and CI execution
- live_web: live public web search using a lightweight HTTP search client
- openai: optional AI-backed execution when OpenAI credentials are configured
"""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import json
import os
import re
from typing import Any, Protocol
from urllib import parse, request


class ResearchProvider(Protocol):
    """Provider contract used by EMP-001 to EMP-004."""

    def run(self, employee_id: str, idea: str) -> dict[str, Any]:
        """Return a normalized employee output payload."""


@dataclass(frozen=True)
class WebSearchResult:
    """One public web search result used as evidence."""

    title: str
    url: str
    snippet: str

    def as_dict(self) -> dict[str, str]:
        return {"title": self.title, "url": self.url, "snippet": self.snippet}


class WebSearchClient(Protocol):
    """Search client boundary for live market research."""

    def search(self, query: str, limit: int = 5) -> list[WebSearchResult]:
        """Return public search results for a query."""


@dataclass(frozen=True)
class DuckDuckGoLiteSearchClient:
    """No-key public web search client.

    This client intentionally uses only the Python standard library so Genesis can
    run without extra dependencies. It is suitable for manual/local validation.
    Production deployments should replace it with a governed provider such as a
    paid search API with clearer rate limits and terms.
    """

    timeout_seconds: int = 20

    def search(self, query: str, limit: int = 5) -> list[WebSearchResult]:
        encoded = parse.urlencode({"q": query})
        req = request.Request(
            f"https://duckduckgo.com/html/?{encoded}",
            headers={"User-Agent": "GenesisAI/0.2 (+https://github.com/dhiya003/genesis-ai)"},
            method="GET",
        )
        with request.urlopen(req, timeout=self.timeout_seconds) as response:  # nosec B310 - public search endpoint configured by code
            html = response.read().decode("utf-8", errors="replace")
        return _parse_duckduckgo_results(html, limit=limit)


@dataclass(frozen=True)
class DeterministicResearchProvider:
    """Credential-free provider used for local runs and CI."""

    def run(self, employee_id: str, idea: str) -> dict[str, Any]:
        handlers = {
            "EMP-001": self._trend_analysis,
            "EMP-002": self._competitor_analysis,
            "EMP-003": self._customer_analysis,
            "EMP-004": self._product_research,
        }
        if employee_id not in handlers:
            raise ValueError(f"Unknown research employee: {employee_id}")
        return handlers[employee_id](idea)

    def _trend_analysis(self, idea: str) -> dict[str, Any]:
        return {
            "section": "trendAnalysis",
            "score": 78,
            "summary": f"The idea '{idea}' fits a giftable, passion-led niche where content can validate demand before inventory scale.",
            "signals": [
                "Niche communities respond well to identity-led products.",
                "Coffee culture supports repeatable content themes and bundles.",
                "India launch can begin with Instagram and WhatsApp without paid infrastructure.",
            ],
            "evidenceLevel": "model_assumption",
        }

    def _competitor_analysis(self, idea: str) -> dict[str, Any]:
        return {
            "section": "competitorAnalysis",
            "score": 70,
            "summary": f"Competitors for '{idea}' are likely split between generic merchandise sellers and premium coffee accessory brands.",
            "competitorTypes": [
                "Generic print-on-demand merchandise pages",
                "Coffee roasters selling lifestyle accessories",
                "Instagram gifting stores",
            ],
            "differentiation": [
                "Focus on India-specific coffee lover identity.",
                "Bundle products into launch kits instead of selling single commodity items.",
                "Use founder-led validation content before ads.",
            ],
            "evidenceLevel": "model_assumption",
        }

    def _customer_analysis(self, idea: str) -> dict[str, Any]:
        return {
            "section": "customerAnalysis",
            "score": 82,
            "summary": f"Likely customers for '{idea}' are urban coffee drinkers, gifting buyers, and office/home café enthusiasts.",
            "segments": [
                "Young professionals who identify as coffee lovers",
                "Gift buyers looking for affordable premium hampers",
                "Home café creators and content-friendly buyers",
            ],
            "objections": [
                "Price must feel gift-worthy but not luxury-only.",
                "Products must not look like generic marketplace merchandise.",
                "Shipping and packaging quality affect trust.",
            ],
            "evidenceLevel": "model_assumption",
        }

    def _product_research(self, idea: str) -> dict[str, Any]:
        return {
            "section": "productResearch",
            "score": 76,
            "summary": f"The first product set for '{idea}' should be lightweight, visual, easy to ship, and bundle-friendly.",
            "recommendedProducts": [
                "Coffee quote sticker pack",
                "Desk mini print or magnet",
                "Coffee lover gift card",
                "Starter hamper with one hero accessory",
            ],
            "mvpRecommendation": "Launch one compact coffee-lover starter kit and test demand before expanding into mugs, apparel, or heavier products.",
            "evidenceLevel": "model_assumption",
        }


@dataclass(frozen=True)
class LiveWebResearchProvider:
    """Live web-backed provider for Sprint 2 market intelligence."""

    search_client: WebSearchClient

    def run(self, employee_id: str, idea: str) -> dict[str, Any]:
        query = _query_for_employee(employee_id, idea)
        results = self.search_client.search(query, limit=5)
        evidence = [result.as_dict() for result in results]
        score = _score_from_evidence(len(evidence))
        if employee_id == "EMP-001":
            return {
                "section": "trendAnalysis",
                "score": score,
                "summary": _summary("trend signals", idea, evidence),
                "signals": _evidence_snippets(evidence),
                "evidence": evidence,
                "evidenceLevel": "live_web_search",
            }
        if employee_id == "EMP-002":
            return {
                "section": "competitorAnalysis",
                "score": max(45, 100 - score // 3),
                "summary": _summary("competitor landscape", idea, evidence),
                "competitorTypes": _evidence_titles(evidence),
                "differentiation": [
                    "Avoid copying competitor artwork, names, captions, or offer structure.",
                    "Look for underserved price points, bundles, or local cultural positioning.",
                    "Validate with direct customer conversations before inventory spend.",
                ],
                "evidence": evidence,
                "evidenceLevel": "live_web_search",
            }
        if employee_id == "EMP-003":
            return {
                "section": "customerAnalysis",
                "score": score,
                "summary": _summary("customer demand and objections", idea, evidence),
                "segments": [
                    "Buyers and communities visible in live search results",
                    "Gift buyers comparing current offers",
                    "Niche enthusiasts searching for product inspiration",
                ],
                "objections": [
                    "Trust, shipping quality, and uniqueness must be validated manually.",
                    "Search evidence shows interest, not guaranteed purchase intent.",
                ],
                "evidence": evidence,
                "evidenceLevel": "live_web_search",
            }
        if employee_id == "EMP-004":
            return {
                "section": "productResearch",
                "score": score,
                "summary": _summary("product opportunities", idea, evidence),
                "recommendedProducts": _product_ideas_from_evidence(idea, evidence),
                "mvpRecommendation": "Pick one low-cost, easy-to-ship MVP product and validate demand before scaling.",
                "evidence": evidence,
                "evidenceLevel": "live_web_search",
            }
        raise ValueError(f"Unknown research employee: {employee_id}")


@dataclass(frozen=True)
class OpenAIResearchProvider:
    """Optional OpenAI-backed provider using the Responses API over stdlib HTTP."""

    api_key: str
    model: str = "gpt-4.1-mini"

    def run(self, employee_id: str, idea: str) -> dict[str, Any]:
        prompt = _employee_prompt(employee_id, idea)
        payload = {
            "model": self.model,
            "input": prompt,
            "text": {"format": {"type": "json_object"}},
        }
        req = request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=45) as response:  # nosec B310 - fixed trusted API endpoint
            data = json.loads(response.read().decode("utf-8"))
        content = _extract_response_text(data)
        result = json.loads(content)
        result.setdefault("evidenceLevel", "ai_generated")
        return result


def get_research_provider() -> ResearchProvider:
    provider_name = os.environ.get("GENESIS_RESEARCH_PROVIDER", "deterministic").lower()
    if provider_name == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when GENESIS_RESEARCH_PROVIDER=openai")
        return OpenAIResearchProvider(api_key=api_key, model=os.environ.get("GENESIS_RESEARCH_MODEL", "gpt-4.1-mini"))
    if provider_name in {"live", "live_web", "web"}:
        return LiveWebResearchProvider(search_client=DuckDuckGoLiteSearchClient())
    return DeterministicResearchProvider()


def _query_for_employee(employee_id: str, idea: str) -> str:
    if employee_id == "EMP-001":
        return f"{idea} trend demand India market"
    if employee_id == "EMP-002":
        return f"{idea} competitors India products price"
    if employee_id == "EMP-003":
        return f"{idea} customer reviews demand India"
    if employee_id == "EMP-004":
        return f"{idea} product ideas bestseller India"
    raise ValueError(f"Unknown research employee: {employee_id}")


def _score_from_evidence(result_count: int) -> int:
    if result_count >= 5:
        return 78
    if result_count >= 3:
        return 68
    if result_count >= 1:
        return 55
    return 35


def _summary(topic: str, idea: str, evidence: list[dict[str, str]]) -> str:
    if not evidence:
        return f"Live web search found limited evidence for {topic} around '{idea}'. Treat confidence as low and perform manual validation."
    top_titles = "; ".join(item["title"] for item in evidence[:2] if item.get("title"))
    return f"Live web search found current evidence for {topic} around '{idea}'. Top signals: {top_titles}."


def _evidence_titles(evidence: list[dict[str, str]]) -> list[str]:
    return [item["title"] for item in evidence if item.get("title")][:5]


def _evidence_snippets(evidence: list[dict[str, str]]) -> list[str]:
    snippets = [item["snippet"] for item in evidence if item.get("snippet")]
    return snippets[:5] or _evidence_titles(evidence)


def _product_ideas_from_evidence(idea: str, evidence: list[dict[str, str]]) -> list[str]:
    base = [
        "Low-cost starter kit",
        "Sticker or printable accessory pack",
        "Giftable mini bundle",
    ]
    titles = _evidence_titles(evidence)
    return [f"{idea}: {item}" for item in base] + titles[:2]


def _parse_duckduckgo_results(html: str, limit: int) -> list[WebSearchResult]:
    results: list[WebSearchResult] = []
    blocks = re.split(r'<a rel="nofollow" class="result__a"', html)
    for block in blocks[1:]:
        href_match = re.search(r'href="([^"]+)"', block)
        title_match = re.search(r'>(.*?)</a>', block, flags=re.DOTALL)
        snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', block, flags=re.DOTALL)
        if not href_match or not title_match:
            continue
        url = _clean_url(unescape(href_match.group(1)))
        title = _strip_tags(unescape(title_match.group(1))).strip()
        snippet = _strip_tags(unescape(snippet_match.group(1))).strip() if snippet_match else ""
        if title and url:
            results.append(WebSearchResult(title=title, url=url, snippet=snippet))
        if len(results) >= limit:
            break
    return results


def _clean_url(url: str) -> str:
    if "uddg=" in url:
        parsed = parse.urlparse(url)
        params = parse.parse_qs(parsed.query)
        if params.get("uddg"):
            return params["uddg"][0]
    return url


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value).replace("  ", " ")


def _employee_prompt(employee_id: str, idea: str) -> str:
    section_map = {
        "EMP-001": "trendAnalysis",
        "EMP-002": "competitorAnalysis",
        "EMP-003": "customerAnalysis",
        "EMP-004": "productResearch",
    }
    section = section_map.get(employee_id)
    if not section:
        raise ValueError(f"Unknown research employee: {employee_id}")
    return (
        "You are a Genesis AI research employee. Return JSON only. "
        f"Employee: {employee_id}. Section: {section}. Founder idea: {idea}. "
        "Return keys: section, score, summary, evidenceLevel, plus 2-4 section-specific arrays. "
        "score must be 0-100. evidenceLevel must explain whether the output is live evidence, AI inference, or assumption."
    )


def _extract_response_text(data: dict[str, Any]) -> str:
    if "output_text" in data:
        return str(data["output_text"])
    chunks: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                chunks.append(str(content.get("text", "")))
    if not chunks:
        raise RuntimeError("OpenAI response did not include output text")
    return "".join(chunks)

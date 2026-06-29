"""Research execution providers for Genesis employees.

Sprint 2 must stay executable in CI without external credentials. The default
provider is deterministic. When `GENESIS_RESEARCH_PROVIDER=openai` and
`OPENAI_API_KEY` are available, the same employee contract can call OpenAI.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Protocol
from urllib import request


class ResearchProvider(Protocol):
    """Provider contract used by EMP-001 to EMP-004."""

    def run(self, employee_id: str, idea: str) -> dict[str, Any]:
        """Return a normalized employee output payload."""


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
        with request.urlopen(req, timeout=45) as response:  # fixed trusted API endpoint
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
    return DeterministicResearchProvider()


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

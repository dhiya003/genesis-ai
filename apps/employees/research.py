"""Deterministic research employees for Sprint 2 e2e execution."""

from __future__ import annotations

from typing import Any

EMPLOYEES = ["EMP-001", "EMP-002", "EMP-003", "EMP-004"]


def run_employee(employee_id: str, project: dict[str, Any]) -> dict[str, Any]:
    idea = project["idea"]
    handlers = {
        "EMP-001": _trend_analysis,
        "EMP-002": _competitor_analysis,
        "EMP-003": _customer_analysis,
        "EMP-004": _product_research,
    }
    if employee_id not in handlers:
        raise ValueError(f"Unknown research employee: {employee_id}")
    output = handlers[employee_id](idea)
    output.update({
        "employeeId": employee_id,
        "projectId": project["id"],
        "workflowId": project["workflowId"],
        "status": "COMPLETED",
    })
    return output


def _trend_analysis(idea: str) -> dict[str, Any]:
    return {
        "section": "trendAnalysis",
        "score": 78,
        "summary": f"The idea '{idea}' fits a giftable, passion-led niche where content can validate demand before inventory scale.",
        "signals": [
            "Niche communities respond well to identity-led products.",
            "Coffee culture supports repeatable content themes and bundles.",
            "India launch can begin with Instagram and WhatsApp without paid infrastructure.",
        ],
    }


def _competitor_analysis(idea: str) -> dict[str, Any]:
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
    }


def _customer_analysis(idea: str) -> dict[str, Any]:
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
    }


def _product_research(idea: str) -> dict[str, Any]:
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
    }

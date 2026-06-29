"""Manual Product Factory runner for Sprint 2.

The runner is deterministic and standard-library only. It converts a founder
requirement into a schema-aligned launch pack that can be refined by later AI
employees without blocking Phase 1 manual execution.
"""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
import re
from typing import Any
from uuid import NAMESPACE_URL, uuid5

LAUNCH_PACK_VERSION = "0.1.0"


def _clean_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        raise ValueError("Requirement text cannot be empty")
    return normalized


def _project_id(requirement: str) -> str:
    digest = sha256(requirement.encode("utf-8")).hexdigest()
    return str(uuid5(NAMESPACE_URL, f"genesis-ai:launch-pack:{digest}"))


def _short_name(requirement: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", requirement)
    selected = words[:6] or ["Genesis", "Launch", "Pack"]
    return " ".join(selected).title()


def build_launch_pack(requirement_text: str) -> dict[str, Any]:
    """Build a complete Phase 1 launch pack from a founder requirement."""

    requirement = _clean_text(requirement_text)
    project_id = _project_id(requirement)
    title = _short_name(requirement)
    now = datetime.now(UTC).replace(microsecond=0).isoformat()

    return {
        "reportType": "LAUNCH_PACK",
        "projectId": project_id,
        "version": LAUNCH_PACK_VERSION,
        "createdAt": now,
        "founderRequirement": requirement,
        "projectTitle": title,
        "phase1Manual": True,
        "sections": {
            "research": {
                "summary": f"Validate demand for: {requirement}",
                "targetCustomerHypotheses": [
                    "Buyers already searching for a fast, low-risk solution.",
                    "Instagram and WhatsApp-first customers who need proof before purchase.",
                ],
                "competitorChecks": [
                    "Search Instagram reels/posts for similar offers and note price bands.",
                    "Check Amazon/Meesho/Etsy listings for commodity pressure.",
                    "Record at least 10 competitor hooks, prices, and review complaints.",
                ],
                "assumptions": [
                    "Market truth must be verified manually before scaling ads.",
                    "The first version should avoid paid infrastructure dependencies.",
                ],
            },
            "product": {
                "offer": title,
                "mvpScope": [
                    "One clear starter offer.",
                    "One order/lead collection flow.",
                    "One 7-day validation scorecard.",
                ],
                "pricingStrategy": {
                    "method": "cost-plus and competitor-anchor check",
                    "launchRule": "Start with an introductory price only if margin remains positive after packaging and shipping.",
                },
            },
            "creative": {
                "brandDirection": "trustworthy, clear, founder-led, launch-ready",
                "contentAssets": [
                    "1 product promise post",
                    "1 how-it-works carousel",
                    "1 proof/behind-the-scenes reel",
                    "1 FAQ story set",
                ],
            },
            "marketing": {
                "channels": ["Instagram", "WhatsApp", "Google Form or manual lead sheet"],
                "firstSevenDays": [
                    "Day 1: publish problem/promise post and collect interest.",
                    "Day 2: publish product explanation and DM warm leads.",
                    "Day 3: post proof, pricing, and limited launch slot.",
                    "Day 4: collect objections and update FAQ.",
                    "Day 5: run small manual outreach batch.",
                    "Day 6: publish customer/validation update.",
                    "Day 7: decide continue, change offer, or stop.",
                ],
            },
            "publishing": {
                "manualSteps": [
                    "Create Instagram post/story assets from creative section.",
                    "Publish with a clear comment/DM call to action.",
                    "Track every lead in the lead tracker template.",
                    "Use WhatsApp for confirmation and payment instructions.",
                ],
                "automationReadyLater": True,
            },
            "validation": {
                "successMetrics": [
                    "20 qualified profile visits or DMs",
                    "5 serious enquiries",
                    "1 paid order or clear preorder intent",
                ],
                "killCriteria": [
                    "No qualified enquiries after 7 focused days.",
                    "Customers only want a price below viable margin.",
                ],
            },
        },
        "risks": [
            "Demand may be overestimated without live competitor and customer checks.",
            "Manual fulfillment can break if order tracking is not updated daily.",
            "Creative may need iteration before paid ads make sense.",
        ],
        "nextActions": [
            "Complete competitor check.",
            "Prepare the first offer asset.",
            "Publish and track leads for 7 days.",
        ],
    }

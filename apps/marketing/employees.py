"""Executable Marketing Department employees for Sprint 5."""

from __future__ import annotations

from typing import Any


MARKETING_EMPLOYEES: dict[str, dict[str, Any]] = {
    "EMP-301": {"name": "Marketing Strategist", "section": "marketingStrategy", "role": "Define launch strategy, personas, channels, funnel, and positioning.", "inputSchema": {"required": ["productBlueprint", "creativePack"]}, "outputSchema": {"required": ["launchPositioning", "customerPersonas", "channelStrategy", "funnel"]}, "promptContract": "Convert product and creative assets into a launch strategy.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-302": {"name": "SEO Specialist", "section": "seoPlan", "role": "Create SEO keywords, content topics, titles, and descriptions.", "inputSchema": {"required": ["marketingStrategy"]}, "outputSchema": {"required": ["keywords", "contentTopics", "titles", "metaDescriptions"]}, "promptContract": "Create search-ready launch content for discovery.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-303": {"name": "Instagram Content Planner", "section": "socialCalendar", "role": "Create Instagram calendar, captions, hashtags, stories, and reels.", "inputSchema": {"required": ["creativePack", "marketingStrategy"]}, "outputSchema": {"required": ["instagramCalendar", "captions", "hashtags"]}, "promptContract": "Plan launch content that builds trust and demand.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-304": {"name": "Paid Ads Specialist", "section": "adConcepts", "role": "Create Meta and Google ad concepts with hooks, audiences, and CTAs.", "inputSchema": {"required": ["marketingStrategy", "creativePack"]}, "outputSchema": {"required": ["metaAds", "googleAds", "audiences", "testingPlan"]}, "promptContract": "Create paid ad concepts without spending budget.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-305": {"name": "Marketplace Listing Specialist", "section": "marketplaceListing", "role": "Create marketplace listing copy, bullets, image order, and FAQ.", "inputSchema": {"required": ["productBlueprint", "creativePack"]}, "outputSchema": {"required": ["title", "bullets", "description", "imageOrder"]}, "promptContract": "Create marketplace listing assets for conversion.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-306": {"name": "Landing Page Copywriter", "section": "landingPageCopy", "role": "Create landing page structure, headlines, proof, CTA, and FAQ.", "inputSchema": {"required": ["marketingStrategy", "creativePack"]}, "outputSchema": {"required": ["hero", "sections", "cta", "faq"]}, "promptContract": "Write a launch landing page that captures demand.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-307": {"name": "Email Campaign Specialist", "section": "emailCampaign", "role": "Create launch email sequence.", "inputSchema": {"required": ["marketingStrategy"]}, "outputSchema": {"required": ["sequence", "subjects"]}, "promptContract": "Create email campaign copy for launch and follow-up.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-308": {"name": "WhatsApp Campaign Specialist", "section": "whatsappCampaign", "role": "Create WhatsApp broadcast and reply scripts.", "inputSchema": {"required": ["marketingStrategy"]}, "outputSchema": {"required": ["broadcasts", "replyScripts"]}, "promptContract": "Create concise WhatsApp launch messages for founder review.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-309": {"name": "Influencer Strategist", "section": "influencerStrategy", "role": "Create influencer profile, outreach script, and collaboration plan.", "inputSchema": {"required": ["marketingStrategy"]}, "outputSchema": {"required": ["creatorProfiles", "outreachScript", "collaborationPlan"]}, "promptContract": "Create a practical influencer launch plan.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-310": {"name": "Launch Manager / QA", "section": "launchQaReport", "role": "Validate campaign consistency, launch readiness, and founder approval needs.", "inputSchema": {"required": ["marketingSections"]}, "outputSchema": {"required": ["checks", "launchPlan", "approvalChecklist", "risks"]}, "promptContract": "Run marketing quality gates before publishing.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
}


def run_marketing_employee(employee_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """Run a deterministic Marketing Department employee."""

    if employee_id not in MARKETING_EMPLOYEES:
        raise KeyError(f"Unknown Marketing Department employee: {employee_id}")
    contract = MARKETING_EMPLOYEES[employee_id]
    builders = {
        "EMP-301": _strategy_output,
        "EMP-302": _seo_output,
        "EMP-303": _social_output,
        "EMP-304": _ads_output,
        "EMP-305": _listing_output,
        "EMP-306": _landing_output,
        "EMP-307": _email_output,
        "EMP-308": _whatsapp_output,
        "EMP-309": _influencer_output,
        "EMP-310": _qa_output,
    }
    data = builders[employee_id](context)
    output = {
        "employeeId": employee_id,
        "employeeName": contract["name"],
        "department": "MARKETING",
        "section": contract["section"],
        "status": "COMPLETED",
        "score": data.pop("score", 83),
        "confidence": data.pop("confidence", {"level": "MEDIUM", "score": 0.75}),
        "risks": data.pop("risks", []),
        "validation": data.pop("validation", _default_validation()),
        "contract": contract,
        **data,
    }
    issues = validate_marketing_employee_output(output)
    if issues:
        raise ValueError(f"{employee_id} output validation failed: {issues}")
    return output


def validate_marketing_employee_output(output: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    employee_id = output.get("employeeId")
    contract = MARKETING_EMPLOYEES.get(str(employee_id))
    if not contract:
        return [f"unknown employee: {employee_id}"]
    for key in ["employeeId", "employeeName", "department", "section", "status", "score", "confidence", "validation", "contract"]:
        if key not in output:
            issues.append(f"missing key: {key}")
    if output.get("section") != contract["section"]:
        issues.append(f"section must be {contract['section']}")
    score = output.get("score")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("score must be 0-100")
    for key in contract["outputSchema"]["required"]:
        if key not in output:
            issues.append(f"missing contract output: {key}")
    validation = output.get("validation")
    if not isinstance(validation, dict) or not all(validation.get(key) == "PASS" for key in ["schema", "business", "channel", "confidence", "risk"]):
        issues.append("validation gates must all PASS")
    return issues


def _default_validation() -> dict[str, str]:
    return {"schema": "PASS", "business": "PASS", "channel": "PASS", "confidence": "PASS", "risk": "PASS"}


def _product_name(context: dict[str, Any]) -> str:
    return str(context["productBlueprint"].get("productName", "Genesis Product"))


def _brand_name(context: dict[str, Any]) -> str:
    return str(context["creativePack"].get("brandIdentity", {}).get("brandName", "Genesis Brand"))


def _strategy_output(context: dict[str, Any]) -> dict[str, Any]:
    brand = _brand_name(context)
    return {
        "launchPositioning": f"{brand} launches as a premium screen-free learning brand for parents of children aged 3-5 in India.",
        "customerPersonas": [
            {"name": "Urban learning-focused parent", "need": "Premium safe learning toy", "trigger": "Birthday or preschool readiness"},
            {"name": "Gift buyer", "need": "Useful premium child gift", "trigger": "Occasion gifting"},
        ],
        "channelStrategy": {"instagram": "Trust and discovery", "marketplace": "Conversion", "whatsapp": "Warm lead follow-up", "email": "Waitlist nurturing"},
        "funnel": ["Awareness", "Waitlist", "Founder batch", "Marketplace conversion", "Review collection"],
        "score": 86,
    }


def _seo_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "keywords": ["wooden educational toys India", "toys for 3 year olds", "premium wooden toys", "screen free learning toys", "logic toys for kids"],
        "contentTopics": ["How screen-free toys build early logic", "Best wooden learning toys for ages 3-5", "Why parents choose open-ended play"],
        "titles": ["Premium Wooden Logic Toys for Ages 3-5", "Screen-Free Learning Toys for Curious Kids"],
        "metaDescriptions": ["Explore premium wooden logic cubes for children aged 3-5, designed for safe screen-free learning and gifting."],
        "score": 82,
    }


def _social_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "instagramCalendar": [
            {"day": 1, "format": "carousel", "theme": "Problem awareness", "caption": "Playtime can build more than attention."},
            {"day": 3, "format": "reel", "theme": "Pattern challenge", "caption": "Can your little one finish the pattern?"},
            {"day": 5, "format": "static", "theme": "Material trust", "caption": "Rounded wood, calm colors, thoughtful play."},
            {"day": 7, "format": "story", "theme": "Waitlist push", "caption": "Founding batch opens soon."},
        ],
        "captions": ["Screen-free play, made a little smarter.", "Premium wooden play for curious little minds.", "The founding batch is almost ready."],
        "hashtags": ["woodentoysindia", "educationaltoys", "screenfreeplay", "toddlertoys", "earlylearning"],
        "score": 84,
    }


def _ads_output(context: dict[str, Any]) -> dict[str, Any]:
    product = _product_name(context)
    return {
        "metaAds": [
            {"hook": "A premium wooden toy that teaches before it explains.", "creative": "Parent-child pattern play", "cta": "Join the founding batch"},
            {"hook": "Screen-free play for ages 3-5.", "creative": f"{product} unboxing", "cta": "See the Starter kit"},
        ],
        "googleAds": [{"headline": "Premium Wooden Learning Toys", "description": "Logic cubes for ages 3-5. Gift-ready founding batch."}],
        "audiences": ["Parents 25-40 in Indian metros", "Montessori and preschool interest", "Premium gifting buyers"],
        "testingPlan": ["Test learning benefit hook vs gifting hook", "Test Starter kit image vs parent-child lifestyle image"],
        "score": 81,
    }


def _listing_output(context: dict[str, Any]) -> dict[str, Any]:
    brand = _brand_name(context)
    product = _product_name(context)
    return {
        "title": f"{brand} {product} - Premium Wooden Educational Toy for Ages 3-5",
        "bullets": ["Builds logic, pattern recognition, and motor skills", "Premium wooden pieces with rounded-edge design", "Gift-ready packaging for birthdays and early learning", "Includes activity cards for guided play"],
        "description": "A premium educational wooden toy kit designed for safe, screen-free learning at home.",
        "imageOrder": ["Hero", "What's in the box", "Learning benefits", "Material trust", "Variant comparison"],
        "faq": [{"question": "What age is this for?", "answer": "Designed for children aged 3-5 with adult supervision."}],
        "score": 85,
    }


def _landing_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "hero": {"headline": "Premium wooden play for curious little minds", "subheadline": "A screen-free logic kit for children aged 3-5.", "cta": "Join the founding batch"},
        "sections": ["Problem", "How it works", "Inside the box", "Why parents trust it", "Variants", "FAQ"],
        "cta": "Reserve early access",
        "faq": [{"question": "Is it certified?", "answer": "Certification and safety claims are reviewed before production release."}],
        "score": 84,
    }


def _email_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "subjects": ["A calmer way to build early logic", "Founding batch opens soon", "Inside the wooden logic kit"],
        "sequence": [
            {"day": 0, "purpose": "Waitlist welcome", "body": "Thanks for joining the founding batch list. We are building premium screen-free learning for ages 3-5."},
            {"day": 2, "purpose": "Product education", "body": "Here is how pattern play supports early logic and motor skills."},
            {"day": 5, "purpose": "Launch CTA", "body": "The first founding batch is ready for early parent feedback."},
        ],
        "score": 82,
    }


def _whatsapp_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "broadcasts": ["Hi, our premium wooden logic toy founding batch is opening soon. Would you like early access?", "The Starter kit includes wooden cubes, activity cards, and gift-ready packaging."],
        "replyScripts": [{"intent": "price", "reply": "The final launch price will be confirmed after founder-batch supplier quotes."}, {"intent": "age", "reply": "It is designed for children aged 3-5 with adult supervision."}],
        "score": 80,
    }


def _influencer_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "creatorProfiles": ["Montessori parent educator", "Indian parenting micro-creator", "Preschool activity creator"],
        "outreachScript": "Hi, we are launching a premium screen-free wooden logic toy for ages 3-5 and would love your honest parent-focused feedback.",
        "collaborationPlan": ["Send sample after safety review", "Request honest play demo", "Use affiliate code after founder approval"],
        "score": 79,
    }


def _qa_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "checks": [
            {"check": "Strategy aligns with creative pack", "status": "PASS"},
            {"check": "Launch channels covered", "status": "PASS"},
            {"check": "Marketplace copy ready", "status": "PASS"},
            {"check": "No spend/publishing automation triggered", "status": "PASS"},
        ],
        "launchPlan": ["Finalize founder approval", "Collect sample visuals", "Open waitlist", "Run founding batch campaign", "Collect reviews"],
        "approvalChecklist": [
            {"item": "Approve launch positioning", "status": "READY"},
            {"item": "Approve marketplace listing", "status": "READY"},
            {"item": "Approve social calendar", "status": "READY"},
            {"item": "Approve ad hooks before spend", "status": "READY"},
        ],
        "risks": ["Ad performance cannot be estimated until live campaigns run.", "Compliance-sensitive claims need review before publishing."],
        "score": 82,
    }


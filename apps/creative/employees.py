"""Executable Creative Department employees for Sprint 4."""

from __future__ import annotations

from typing import Any


CREATIVE_EMPLOYEES: dict[str, dict[str, Any]] = {
    "EMP-201": {
        "name": "Brand Strategist",
        "section": "brandStrategy",
        "role": "Define positioning, audience, promise, personality, and differentiation.",
        "inputSchema": {"required": ["productBlueprint"]},
        "outputSchema": {"required": ["positioning", "targetAudience", "brandPromise", "personality", "differentiation"]},
        "promptContract": "Turn the Product Blueprint into a clear brand strategy.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-202": {
        "name": "Naming Specialist",
        "section": "brandNaming",
        "role": "Generate and recommend brand names aligned to product strategy.",
        "inputSchema": {"required": ["brandStrategy", "productBlueprint"]},
        "outputSchema": {"required": ["nameOptions", "recommendedName", "rationale"]},
        "promptContract": "Create distinct, memorable names that fit the founder opportunity.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-203": {
        "name": "Logo Designer",
        "section": "logoSystem",
        "role": "Define logo direction, mark concept, lockups, and usage rules.",
        "inputSchema": {"required": ["brandNaming", "brandStrategy"]},
        "outputSchema": {"required": ["primaryConcept", "secondaryConcept", "iconMark", "usage"]},
        "promptContract": "Create a production-ready logo system brief.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-204": {
        "name": "Visual Identity Designer",
        "section": "visualIdentity",
        "role": "Define colors, typography, visual language, and brand rules.",
        "inputSchema": {"required": ["logoSystem", "brandStrategy"]},
        "outputSchema": {"required": ["colorPalette", "typography", "visualRules"]},
        "promptContract": "Create a cohesive visual identity for packaging and launch assets.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-205": {
        "name": "Packaging Designer",
        "section": "packagingDesignBrief",
        "role": "Translate packaging engineering into creative packaging direction.",
        "inputSchema": {"required": ["productBlueprint", "visualIdentity"]},
        "outputSchema": {"required": ["concept", "panelContent", "materials", "compliancePlaceholders"]},
        "promptContract": "Create a supplier-ready packaging design brief.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-206": {
        "name": "Product Mockup Designer",
        "section": "productMockupBrief",
        "role": "Define product, variant, and lifestyle mockup scenes.",
        "inputSchema": {"required": ["productBlueprint", "visualIdentity"]},
        "outputSchema": {"required": ["variantMockups", "lifestyleScenes", "renderingGuidance"]},
        "promptContract": "Create image-generation-ready mockup briefs for each product variant.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-207": {
        "name": "Marketplace Creative Designer",
        "section": "marketplaceCreativePack",
        "role": "Define marketplace hero, feature, comparison, and trust images.",
        "inputSchema": {"required": ["productBlueprint", "copyAssets"]},
        "outputSchema": {"required": ["imageConcepts", "requirements", "qualityRules"]},
        "promptContract": "Create marketplace-ready creative concepts for conversion.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-208": {
        "name": "Social Media Designer",
        "section": "socialMediaCreativePack",
        "role": "Define Instagram posts, stories, reels, and launch banners.",
        "inputSchema": {"required": ["brandStrategy", "visualIdentity"]},
        "outputSchema": {"required": ["instagramPosts", "stories", "reels", "launchBanners"]},
        "promptContract": "Create platform-ready social creative concepts.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-209": {
        "name": "Copywriter",
        "section": "copyAssets",
        "role": "Write taglines, packaging copy, product copy, captions, and listing copy.",
        "inputSchema": {"required": ["brandStrategy", "productBlueprint"]},
        "outputSchema": {"required": ["taglines", "packagingCopy", "productHeadline", "featureBullets", "socialCaptions"]},
        "promptContract": "Write clear, conversion-aware launch copy in the brand voice.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-210": {
        "name": "Creative Director / QA",
        "section": "creativeQaReport",
        "role": "Validate creative consistency, launch readiness, and founder approval needs.",
        "inputSchema": {"required": ["creativeSections"]},
        "outputSchema": {"required": ["checks", "approvalChecklist", "risks"]},
        "promptContract": "Run creative quality gates and summarize founder approval needs.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
}


def run_creative_employee(employee_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """Run a deterministic Creative Department employee."""

    if employee_id not in CREATIVE_EMPLOYEES:
        raise KeyError(f"Unknown Creative Department employee: {employee_id}")
    contract = CREATIVE_EMPLOYEES[employee_id]
    builders = {
        "EMP-201": _brand_strategy_output,
        "EMP-202": _naming_output,
        "EMP-203": _logo_output,
        "EMP-204": _visual_identity_output,
        "EMP-205": _packaging_output,
        "EMP-206": _mockup_output,
        "EMP-207": _marketplace_output,
        "EMP-208": _social_output,
        "EMP-209": _copy_output,
        "EMP-210": _qa_output,
    }
    data = builders[employee_id](context)
    output = {
        "employeeId": employee_id,
        "employeeName": contract["name"],
        "department": "CREATIVE",
        "section": contract["section"],
        "status": "COMPLETED",
        "score": data.pop("score", 84),
        "confidence": data.pop("confidence", {"level": "MEDIUM", "score": 0.76}),
        "risks": data.pop("risks", []),
        "validation": data.pop("validation", _default_validation()),
        "contract": contract,
        **data,
    }
    issues = validate_creative_employee_output(output)
    if issues:
        raise ValueError(f"{employee_id} output validation failed: {issues}")
    return output


def validate_creative_employee_output(output: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    employee_id = output.get("employeeId")
    contract = CREATIVE_EMPLOYEES.get(str(employee_id))
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
    if not isinstance(validation, dict) or not all(validation.get(key) == "PASS" for key in ["schema", "brand", "creative", "confidence", "risk"]):
        issues.append("validation gates must all PASS")
    return issues


def _default_validation() -> dict[str, str]:
    return {"schema": "PASS", "brand": "PASS", "creative": "PASS", "confidence": "PASS", "risk": "PASS"}


def _blueprint(context: dict[str, Any]) -> dict[str, Any]:
    return context["productBlueprint"]


def _product_name(context: dict[str, Any]) -> str:
    return str(_blueprint(context).get("productName", "Genesis Product"))


def _is_wooden_toy(context: dict[str, Any]) -> bool:
    source = " ".join(
        [
            str(_blueprint(context).get("sourceIdea", "")),
            str(_blueprint(context).get("productName", "")),
            str(_blueprint(context).get("productDefinition", {}).get("category", "")),
        ]
    ).lower()
    return "wood" in source or "toy" in source or "children" in source or "kids" in source or "3-5" in source


def _brand_strategy_output(context: dict[str, Any]) -> dict[str, Any]:
    toy = _is_wooden_toy(context)
    return {
        "brandPurpose": "Make early learning feel beautiful, safe, and useful at home." if toy else "Turn a validated product opportunity into a trustworthy launch brand.",
        "brandMission": "Help families choose purposeful, screen-free play with confidence." if toy else "Help founders launch a clear first product with strong brand trust.",
        "brandVision": "Become India's most trusted premium early-learning play brand." if toy else "Become a repeatable brand system for product-family launches.",
        "valueProposition": "Premium wooden learning products that combine parent trust, child engagement, and gift-ready presentation." if toy else "A simple, polished product brand built for validation and scale.",
        "emotionalPositioning": "Calm confidence for parents and joyful discovery for children." if toy else "Practical confidence for early buyers.",
        "competitivePositioning": "More premium and intentional than generic marketplace toys; more accessible than imported educational systems." if toy else "More structured than generic marketplace listings.",
        "brandArchetype": "Caregiver Sage" if toy else "Creator Guide",
        "positioning": "Premium screen-free learning toys for early childhood development in India" if toy else "A focused launch brand built around the validated product opportunity",
        "targetAudience": _blueprint(context).get("customerFit", {}).get("targetCustomer", {}),
        "brandPromise": "Beautiful play that quietly builds logic, motor skills, and confidence." if toy else "A clear first product with a trustworthy story and polished launch presence.",
        "personality": ["warm", "intelligent", "safe", "premium", "playful"] if toy else ["focused", "useful", "modern", "trustworthy"],
        "differentiation": "Combines premium natural materials, parent-friendly education value, and gift-ready presentation." if toy else "Uses a product-family story instead of generic marketplace positioning.",
        "toneOfVoice": "Calm, parent-friendly, clear, and lightly playful",
        "score": 88,
    }


def _naming_output(context: dict[str, Any]) -> dict[str, Any]:
    toy = _is_wooden_toy(context)
    options = ["LumaLearn", "TinkerLuma", "Little Logic Co"] if toy else ["Foundry Goods", "Pilot & Pack", "Bright Batch"]
    return {
        "nameOptions": options,
        "recommendedName": options[0],
        "rationale": "Short, memorable, warm, and extendable across future learning products." if toy else "Simple and broad enough for a product-family roadmap.",
        "rejectedNames": [{"name": name, "reason": "Good backup, but less direct than the recommended name."} for name in options[1:]],
        "score": 86,
    }


def _logo_output(context: dict[str, Any]) -> dict[str, Any]:
    name = context["sections"]["brandNaming"]["recommendedName"]
    return {
        "primaryConcept": f"{name} wordmark with a small cube/sun learning mark.",
        "secondaryConcept": "Stacked lockup for square packaging and marketplace thumbnails.",
        "iconMark": "Rounded cube with three simple path lines suggesting logic and play.",
        "monochromeVersion": "Single-color mark for box stamping and instruction cards.",
        "usage": {"lightBackground": "Use forest green wordmark.", "darkBackground": "Use warm ivory mark.", "minimumSize": "24 mm wide on packaging."},
        "score": 84,
    }


def _visual_identity_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "colorPalette": [
            {"name": "Forest Green", "hex": "#1F5A46", "usage": "Primary brand color"},
            {"name": "Marigold", "hex": "#F4B740", "usage": "Learning accent"},
            {"name": "Warm Ivory", "hex": "#FFF7E6", "usage": "Packaging base"},
            {"name": "Soft Coral", "hex": "#E87561", "usage": "Variant accent"},
            {"name": "Ink Charcoal", "hex": "#242424", "usage": "Text"},
        ],
        "typography": {"heading": "Rounded geometric sans", "body": "Readable humanist sans", "packaging": "Large friendly headings with concise parent-facing proof points"},
        "visualRules": ["Use real product visibility", "Keep claims parent-clear", "Avoid cluttered educational jargon", "Show hands, scale, and activity cards"],
        "graphicStyle": "Soft geometric patterns inspired by cubes, paths, and early learning shapes",
        "score": 85,
    }


def _packaging_output(context: dict[str, Any]) -> dict[str, Any]:
    name = context["sections"]["brandNaming"]["recommendedName"]
    return {
        "concept": f"{name} premium learning kit box with natural board texture and bold color-coded variant band.",
        "panelContent": {
            "front": ["Brand name", "Product name", "Age 3-5", "Logic + motor skills benefit", "Product window or product render"],
            "back": ["How children play", "What is inside", "Parent benefit proof", "Safety placeholders"],
            "side": ["Variant name", "SKU placeholder", "QR placeholder", "Barcode placeholder"],
        },
        "materials": ["Rigid kraft board", "Paper pulp insert", "Matte water-based finish"],
        "finishRecommendations": ["Matte lamination alternative", "Single spot-color accent", "Stamped monochrome logo option"],
        "compliancePlaceholders": ["Age grade", "Choking hazard review", "Non-toxic paint claim pending certification", "Manufacturer details"],
        "sustainabilityNotes": "Plastic-free, recyclable paper components, compact shipping footprint.",
        "score": 86,
    }


def _mockup_output(context: dict[str, Any]) -> dict[str, Any]:
    product_name = _product_name(context)
    return {
        "variantMockups": [
            {"variant": "Starter", "brief": f"{product_name} Starter box, six cubes, activity cards, warm tabletop light."},
            {"variant": "Standard", "brief": f"{product_name} Standard kit with expanded cubes and parent guide."},
            {"variant": "Premium", "brief": f"{product_name} Premium gift-ready box with complete family set."},
        ],
        "lifestyleScenes": ["Parent and child solving a simple pattern", "Gift box opened on a clean Indian home table", "Close-up of safe rounded wooden edges"],
        "renderingGuidance": "Use bright natural light, visible product scale, no exaggerated claims, no unsafe small loose parts near younger children.",
        "marketplaceImageRequirements": ["White-background hero", "Scale image", "What's in the box", "Skill benefits", "Safety and material proof"],
        "score": 84,
    }


def _marketplace_output(context: dict[str, Any]) -> dict[str, Any]:
    product_name = _product_name(context)
    return {
        "imageConcepts": [
            {"slot": 1, "title": "Hero product image", "brief": f"{product_name} box, cubes, and activity cards arranged clearly on white."},
            {"slot": 2, "title": "Learning benefits", "brief": "Three benefit tiles: logic, motor skills, pattern recognition."},
            {"slot": 3, "title": "Material trust", "brief": "Close-up of wood grain, rounded edges, paint safety placeholder."},
            {"slot": 4, "title": "Variant comparison", "brief": "Starter vs Standard vs Premium contents grid."},
        ],
        "requirements": ["Readable on mobile", "Product visible in every image", "No unsupported certification claims"],
        "qualityRules": ["Avoid tiny text", "Avoid clutter", "Keep parent benefit above feature detail"],
        "score": 83,
    }


def _social_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "instagramPosts": [
            {"format": "carousel", "hook": "A toy that teaches before it explains.", "slides": ["Problem", "How it works", "Skills built", "Inside the box", "Founder waitlist CTA"]},
            {"format": "static", "hook": "Premium wooden play for curious little minds.", "visual": "Child hand arranging cubes with parent nearby"},
        ],
        "stories": ["Poll: Which skill should playtime build?", "Behind the product: why rounded wooden cubes", "Waitlist sticker"],
        "reels": ["15-second pattern challenge", "Unbox the Starter kit", "Parent explains screen-free play"],
        "launchBanners": ["Founding batch now open", "Built for ages 3-5", "Starter, Standard, Premium kits"],
        "score": 84,
    }


def _copy_output(context: dict[str, Any]) -> dict[str, Any]:
    name = context["sections"].get("brandNaming", {}).get("recommendedName", "Genesis Brand")
    return {
        "taglines": ["Play that builds little logic.", "Quiet learning. Beautiful play.", "Premium wooden play for curious minds."],
        "packagingCopy": {"front": f"{name} Logic Cubes", "back": "A premium wooden activity kit designed to help children explore patterns, logic, and motor skills through screen-free play."},
        "productHeadline": "Premium wooden logic cubes for children aged 3-5",
        "productDescription": "A gift-ready educational wooden toy kit for parents who want safe, beautiful, screen-free learning at home.",
        "featureBullets": ["Supports logic and pattern recognition", "Rounded wooden pieces for comfortable play", "Gift-ready packaging", "Expandable activity system"],
        "socialCaptions": ["Screen-free play, made a little smarter.", "A calmer way to build early logic skills.", "The first founding batch is almost ready."],
        "marketplaceListingDraft": "Premium wooden educational toy kit for ages 3-5 with activity cards, safe rounded pieces, and gift-ready packaging.",
        "score": 85,
    }


def _qa_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "checks": [
            {"check": "Brand-product fit", "status": "PASS"},
            {"check": "Variant coverage", "status": "PASS"},
            {"check": "Packaging clarity", "status": "PASS"},
            {"check": "Marketplace readiness", "status": "PASS"},
            {"check": "Unsupported claims", "status": "PASS"},
        ],
        "approvalChecklist": [
            {"item": "Approve brand name", "status": "READY"},
            {"item": "Approve logo direction", "status": "READY"},
            {"item": "Approve packaging concept", "status": "READY"},
            {"item": "Approve image-generation briefs", "status": "READY"},
            {"item": "Confirm compliance wording before print", "status": "REVIEW"},
        ],
        "risks": ["Certification claims must remain placeholders until verified.", "Final logo files require design tool production."],
        "score": 82,
    }

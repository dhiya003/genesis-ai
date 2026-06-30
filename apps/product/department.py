"""Product Department Phase 1 execution."""

from __future__ import annotations

import logging
from statistics import mean
from typing import Any

from apps.observability import MetricsRecorder
from apps.storage import JsonStore
from scripts.validate_product_definition import validate_product_definition_payload

LOGGER = logging.getLogger("genesis.product")

OPPORTUNITY_DIMENSIONS = [
    "customerValue",
    "marketGap",
    "competition",
    "manufacturingDifficulty",
    "profit",
    "differentiation",
    "scalability",
    "supplierAvailability",
    "inventoryRisk",
    "shippingRisk",
    "learningValue",
]

PRODUCT_METRIC_KEYS = [
    "complexityScore",
    "manufacturabilityScore",
    "innovationScore",
    "profitabilityScore",
    "customerValueScore",
    "shippingScore",
    "packagingScore",
    "expansionPotential",
]


class ProductDepartment:
    """Converts validated research into Sprint 3 Phase 1 product intelligence."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def execute(self, project: dict[str, Any], workflow: dict[str, Any], research_report: dict[str, Any]) -> dict[str, Any]:
        LOGGER.info("product department started", extra={"event": "product.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        product_definition = self.build_product_definition(project, workflow, research_report)
        validation_issues = validate_product_definition_payload(product_definition)
        if validation_issues:
            raise ValueError(f"Product definition validation failed: {validation_issues}")
        self.store.save_product_definition(product_definition)
        for entry in product_definition["knowledgeBaseEntries"]:
            self.store.save_product_knowledge(entry)
        MetricsRecorder(self.store).record(
            "product.definition_stored",
            {
                "overallProductScore": product_definition["successMetrics"]["overallProductScore"],
                "overallOpportunityScore": product_definition["opportunityReport"]["overallOpportunityScore"],
            },
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("product definition stored", extra={"event": "product.definition_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return product_definition

    def build_product_definition(self, project: dict[str, Any], workflow: dict[str, Any], research_report: dict[str, Any]) -> dict[str, Any]:
        recommended_products = research_report.get("productResearch", {}).get("recommendedProducts", [])
        base_product = _first_text(recommended_products, "starter kit")
        product_name = _product_name(project.get("idea", ""), base_product)
        target_customer = _target_customer(research_report)
        opportunity_scores = _opportunity_scores(research_report)
        product_metrics = _product_metrics(opportunity_scores)
        variants = _variant_matrix(product_name)
        roadmap = _roadmap(product_name)
        constraints = _constraints(project)
        risks = _risk_register(research_report)
        checklist = _approval_checklist()
        product_definition_document = {
            "projectId": project["id"],
            "sourceReportId": research_report["projectId"],
            "productName": product_name,
            "category": _category(project.get("idea", "")),
            "purpose": _purpose(project.get("idea", ""), base_product),
            "problemSolved": "Gives the target customer a clear, giftable, identity-led product instead of generic marketplace merchandise.",
            "targetCustomer": target_customer,
            "ageGroup": target_customer.get("ageGroup", "Adults"),
            "useCase": "Starter purchase, gifting, validation launch, and later product-family expansion.",
            "productStory": f"{product_name} turns the validated research opportunity into a simple product family that can be tested before inventory scale.",
            "differentiator": "A focused starter product with planned variants, lightweight shipping, and a brand story tied to the research insight.",
            "educationalDomain": ["Customer learning", "Market validation", "Product-family testing"],
            "recommendedMaterial": "Lightweight printable or packable materials selected for low-risk MVP validation.",
            "difficulty": "Easy",
            "packagingType": "Starter kit",
            "variants": variants,
            "futureRoadmap": roadmap,
            "evidence": research_report.get("evidence", []),
            "assumptions": [
                "Sprint 3 Phase 1 uses deterministic product intelligence until live supplier data is connected.",
                "Manufacturing, BOM, and supplier validation happen in later Sprint 3 phases.",
                "Founder should validate demand before inventory purchase.",
            ],
        }
        rejected_alternatives = _rejected_alternatives(recommended_products)
        return {
            "reportType": "PRODUCT_DEFINITION",
            "version": "0.3.0",
            "projectId": project["id"],
            "workflowId": workflow["id"],
            "sourceReportId": research_report["projectId"],
            "sourceWorkflowId": research_report["workflowId"],
            "sourceIdea": research_report["idea"],
            "department": "PRODUCT",
            "manager": "PRODUCT_MANAGER",
            "productDefinitionDocument": product_definition_document,
            "opportunityReport": {
                "scores": opportunity_scores,
                "overallOpportunityScore": round(mean(opportunity_scores.values())),
                "rankingRationale": "The selected product balances customer clarity, low manufacturing risk, shipping simplicity, and expansion potential.",
                "selectedOpportunity": product_name,
                "rejectedAlternatives": rejected_alternatives,
                "evidenceReferences": [citation.get("url") or citation.get("source") for citation in research_report.get("citations", [])],
            },
            "variantMatrix": variants,
            "productRoadmap": roadmap,
            "constraintsReport": constraints,
            "successMetrics": product_metrics,
            "riskRegister": risks,
            "approvalChecklist": checklist,
            "knowledgeBaseEntries": _knowledge_entries(project, product_name, rejected_alternatives),
        }


def _first_text(values: list[Any], fallback: str) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _product_name(idea: str, base_product: str) -> str:
    idea_lower = idea.lower()
    if "coffee" in idea_lower:
        return "Brew Buddy Starter Kit"
    if "toy" in idea_lower or "children" in idea_lower or "kids" in idea_lower:
        return "Luma Logic Cubes"
    words = [word.strip(".,") for word in base_product.split() if word.strip(".,")]
    if words:
        return " ".join(word.capitalize() for word in words[:4])
    return "Genesis Starter Product"


def _category(idea: str) -> str:
    idea_lower = idea.lower()
    if "coffee" in idea_lower:
        return "Lifestyle gifting"
    if "toy" in idea_lower or "children" in idea_lower or "kids" in idea_lower:
        return "Educational toy"
    return "Consumer product"


def _purpose(idea: str, base_product: str) -> str:
    if "coffee" in idea.lower():
        return "Help coffee lovers express their identity through an affordable, giftable starter kit."
    return f"Convert the validated market opportunity into a simple, manufacturable {base_product}."


def _target_customer(research_report: dict[str, Any]) -> dict[str, Any]:
    segments = research_report.get("customerAnalysis", {}).get("segments", [])
    primary_segment = _first_text(segments, "Early adopter customer")
    return {
        "primarySegment": primary_segment,
        "buyer": primary_segment,
        "ageGroup": "18-35",
        "needs": [
            "Clear product value",
            "Affordable first purchase",
            "Trustworthy packaging and delivery",
        ],
    }


def _opportunity_scores(research_report: dict[str, Any]) -> dict[str, int]:
    base = int(research_report.get("opportunityScore") or research_report.get("overallScore") or 70)
    scores = {
        "customerValue": min(100, base + 6),
        "marketGap": min(100, base + 2),
        "competition": max(0, base - 8),
        "manufacturingDifficulty": 78,
        "profit": min(100, base + 1),
        "differentiation": min(100, base + 4),
        "scalability": min(100, base + 3),
        "supplierAvailability": 72,
        "inventoryRisk": 68,
        "shippingRisk": 82,
        "learningValue": min(100, base + 7),
    }
    return {key: int(scores[key]) for key in OPPORTUNITY_DIMENSIONS}


def _product_metrics(opportunity_scores: dict[str, int]) -> dict[str, int]:
    metrics = {
        "complexityScore": 32,
        "manufacturabilityScore": opportunity_scores["manufacturingDifficulty"],
        "innovationScore": opportunity_scores["differentiation"],
        "profitabilityScore": opportunity_scores["profit"],
        "customerValueScore": opportunity_scores["customerValue"],
        "shippingScore": opportunity_scores["shippingRisk"],
        "packagingScore": 80,
        "expansionPotential": opportunity_scores["scalability"],
    }
    metrics["overallProductScore"] = round(mean(metrics.values()))
    return metrics


def _variant_matrix(product_name: str) -> list[dict[str, Any]]:
    return [
        {"level": "Starter", "name": f"{product_name} Starter", "contents": ["Core product", "Simple packaging"], "purpose": "Validate demand with minimum inventory risk"},
        {"level": "Standard", "name": f"{product_name} Standard", "contents": ["Core product", "Bonus item", "Gift-ready packaging"], "purpose": "Increase perceived value"},
        {"level": "Premium", "name": f"{product_name} Premium", "contents": ["Expanded product set", "Premium packaging"], "purpose": "Serve gifting and higher-margin buyers"},
        {"level": "Bundle", "name": f"{product_name} Bundle", "contents": ["Multiple units", "Occasion-based bundle"], "purpose": "Raise average order value"},
        {"level": "Subscription", "name": f"{product_name} Club", "contents": ["Recurring monthly variation"], "purpose": "Test repeat purchase potential"},
        {"level": "Accessories", "name": f"{product_name} Accessories", "contents": ["Replacement or add-on parts"], "purpose": "Create low-cost upsells"},
        {"level": "Expansion Packs", "name": f"{product_name} Expansion Pack", "contents": ["New themes", "Advanced variants"], "purpose": "Build a product family"},
    ]


def _roadmap(product_name: str) -> dict[str, Any]:
    return {
        "version1": f"{product_name} Starter validation kit",
        "version2": "Gift-ready standard kit with improved packaging",
        "version3": "Premium bundle with stronger brand story and add-ons",
        "futureFeatures": ["Seasonal themes", "Personalization", "Limited editions"],
        "accessories": ["Replacement parts", "Add-on cards", "Gift wrap"],
        "digitalCompanion": "Landing page with founder story, waitlist, and customer feedback capture",
        "subscription": "Monthly themed drop if repeat demand is validated",
        "expansionOpportunities": ["Bundles", "Corporate gifting", "Retail-ready packaging"],
    }


def _constraints(project: dict[str, Any]) -> dict[str, Any]:
    return {
        "founderBudget": project.get("budget") or "Not specified",
        "country": project.get("country") or "Not specified",
        "manufacturingCapability": "Start with simple, low-tooling production until demand is proven.",
        "moq": "Prefer low MOQ or manual pilot batch.",
        "machineAvailability": "Avoid machine-dependent design in Phase 1.",
        "shipping": "Keep the starter variant lightweight and compact.",
        "storage": "Avoid bulky or fragile inventory.",
        "safety": "Validate category-specific safety and labeling before production.",
        "targetMargin": "Target 55-65 percent gross margin before paid ads.",
        "timeToMarket": project.get("timeline") or "Pilot within 2-4 weeks",
        "constraints": project.get("constraints", []),
    }


def _risk_register(research_report: dict[str, Any]) -> list[dict[str, Any]]:
    source_risks = research_report.get("risks", [])
    risks = [
        {"risk": _first_text(source_risks[:1], "Demand may not convert into purchases."), "severity": "HIGH", "mitigation": "Run a manual validation launch before inventory purchase."},
        {"risk": "Product may look generic without a strong differentiator.", "severity": "MEDIUM", "mitigation": "Use variant strategy, packaging, and story to sharpen differentiation."},
        {"risk": "Unit economics may fail after packaging and shipping.", "severity": "HIGH", "mitigation": "Complete Sprint 3 cost engineering before supplier commitment."},
    ]
    return risks


def _approval_checklist() -> list[dict[str, Any]]:
    return [
        {"item": "Solves a real problem", "status": "PASS", "evidence": "Research report recommendation supports lean validation."},
        {"item": "Buyer can understand quickly", "status": "PASS", "evidence": "Product definition uses a starter kit and clear purpose."},
        {"item": "Can be manufactured", "status": "PASS", "evidence": "Phase 1 keeps the product simple and low-tooling."},
        {"item": "Can be shipped", "status": "PASS", "evidence": "Variant matrix prioritizes compact starter packaging."},
        {"item": "Can scale", "status": "PASS", "evidence": "Roadmap includes standard, premium, bundle, and expansion paths."},
        {"item": "Can be branded", "status": "PASS", "evidence": "Product story and differentiator are explicit."},
        {"item": "Can become a product family", "status": "PASS", "evidence": "Variants include accessories, subscription, and expansion packs."},
    ]


def _rejected_alternatives(recommended_products: list[Any]) -> list[dict[str, str]]:
    alternatives = [value for value in recommended_products[1:] if isinstance(value, str) and value.strip()]
    if not alternatives:
        alternatives = ["Heavy inventory product", "Generic single-item merchandise"]
    return [
        {"name": alternative, "reason": "Rejected for Phase 1 because it creates higher inventory, differentiation, or validation risk."}
        for alternative in alternatives[:3]
    ]


def _knowledge_entries(project: dict[str, Any], product_name: str, rejected_alternatives: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "projectId": project["id"],
            "type": "GENERATED_PRODUCT",
            "productName": product_name,
            "lesson": "Start with a compact product family seed instead of a single-product dead end.",
            "futureImprovement": "Re-score after supplier, BOM, and packaging data are available.",
        },
        {
            "projectId": project["id"],
            "type": "REJECTED_PRODUCTS",
            "productName": "Rejected alternatives",
            "rejectedProducts": rejected_alternatives,
            "lesson": "Weak alternatives should be retained with reasons so future product decisions improve.",
            "futureImprovement": "Revisit alternatives if manufacturing or supplier constraints change.",
        },
    ]

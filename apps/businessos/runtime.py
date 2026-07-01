"""BusinessOS runtime foundation for Sprint 8.

The deterministic MVP creates an auditable operating context from the launch
package. It does not bypass approval policy or perform live irreversible actions.
"""

from __future__ import annotations

from statistics import mean
from typing import Any

from apps.audit import now_iso
from apps.storage import JsonStore
from scripts.validate_business_operating_plan import validate_business_operating_plan_payload


class BusinessOSRuntime:
    """Builds the first BusinessOS operating plan from prior sprint artifacts."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def execute(self, project: dict[str, Any], workflow: dict[str, Any], launch_package: dict[str, Any]) -> dict[str, Any]:
        product_blueprint = self.store.get_product_blueprint(launch_package["productId"])
        creative_pack = self.store.get_creative_pack(launch_package["creativeId"])
        marketing_pack = self.store.get_marketing_pack(launch_package["marketingId"])
        research_report = self.store.get_report(project["id"])

        digital_twin = _digital_twin(project, research_report, product_blueprint, creative_pack, marketing_pack, launch_package)
        health = _business_health(launch_package, marketing_pack, product_blueprint)
        knowledge_graph = _knowledge_graph(project, research_report, product_blueprint, creative_pack, marketing_pack, launch_package)
        simulations = _simulations(product_blueprint, marketing_pack)
        decisions = _decision_register(launch_package, simulations)
        recommendations = _recommendations(health, simulations, launch_package)
        learning = _learning_engine(project, launch_package)
        resource_plan = _resource_plan(project, product_blueprint, marketing_pack)

        plan = {
            "reportType": "BUSINESS_OPERATING_PLAN",
            "version": "1.0.0-foundation",
            "projectId": project["id"],
            "businessId": project["id"],
            "launchId": launch_package["launchId"],
            "workflowId": workflow["id"],
            "department": "BUSINESS_OS",
            "runtime": "Genesis CEO Runtime",
            "createdAt": now_iso(),
            "founderVision": {
                "idea": project.get("idea"),
                "budget": project.get("budget"),
                "constraints": project.get("constraints", []),
                "timeline": project.get("timeline"),
                "successMetrics": ["monthly revenue", "gross margin", "customer acquisition cost", "repeat purchase rate"],
            },
            "executiveCouncil": _executive_council(),
            "departmentPlans": _department_plans(),
            "crossDepartmentLoop": ["Research", "Product", "Creative", "Marketing", "Sales", "Commerce & Publishing", "Analytics", "Optimization", "Research Again"],
            "strategicPlan": _strategic_plan(project, product_blueprint, marketing_pack),
            "businessPlan": _business_plan(product_blueprint, marketing_pack, launch_package),
            "digitalTwin": digital_twin,
            "knowledgeGraph": knowledge_graph,
            "businessMemory": _business_memory(project, research_report, product_blueprint, creative_pack, marketing_pack, launch_package),
            "portfolioPlan": _portfolio_plan(project),
            "resourcePlan": resource_plan,
            "decisionRegister": decisions,
            "approvalPolicy": _approval_policy(launch_package),
            "simulationResults": simulations,
            "businessHealth": health,
            "opportunities": _opportunities(product_blueprint, marketing_pack),
            "risks": _risks(launch_package, product_blueprint),
            "recommendations": recommendations,
            "learningEngine": learning,
            "selfImprovementPlan": _self_improvement_plan(),
            "integrationRegistry": _integration_registry(),
            "dashboards": _dashboards(),
            "observabilityPlan": _observability_plan(),
            "securityPlan": _security_plan(),
            "governanceBoundaries": [
                "No irreversible action without configured approval policy.",
                "No legal, financial, or ad-spend action without founder or delegated human approval.",
                "Self-improvement may improve workflows and prompts but cannot change immutable governance rules.",
            ],
            "nextActions": [
                "Implement Sprint 7 live metrics ingestion for continuous monitoring.",
                "Connect publishing integrations behind approval gates.",
                "Create founder dashboard over BusinessOS plan, health, decisions, and recommendations.",
            ],
            "overallScore": round(mean([health["overallBusinessHealthScore"], launch_package["overallScore"], product_blueprint.get("overallScore", 82)])),
        }
        issues = validate_business_operating_plan_payload(plan)
        if issues:
            raise ValueError(f"Business Operating Plan validation failed: {issues}")

        self.store.save_business_operating_plan(plan)
        self.store.save_digital_twin(plan["businessId"], digital_twin)
        self.store.save_knowledge_graph(plan["businessId"], knowledge_graph)
        self.store.save_decision_register(plan["businessId"], {"businessId": plan["businessId"], "decisions": decisions})
        self.store.save_simulation_report(plan["businessId"], {"businessId": plan["businessId"], "simulations": simulations})
        self.store.save_business_health_report(plan["businessId"], health)
        self.store.save_recommendation_report(plan["businessId"], {"businessId": plan["businessId"], "recommendations": recommendations})
        return plan


def _executive_council() -> list[dict[str, str]]:
    return [
        {"role": "Chief Research Officer", "department": "Research", "mission": "Continuously identify validated opportunities."},
        {"role": "Chief Product Officer", "department": "Product", "mission": "Convert opportunities into manufacturable products."},
        {"role": "Chief Creative Officer", "department": "Creative", "mission": "Create brand and visual assets."},
        {"role": "Chief Marketing Officer", "department": "Marketing", "mission": "Create demand and launch campaigns."},
        {"role": "Chief Sales Officer", "department": "Sales", "mission": "Convert demand into customers, quotes, orders, and revenue."},
        {"role": "Chief Operations Officer", "department": "Commerce & Publishing", "mission": "Coordinate safe execution, catalog publishing, and fulfilment handoff."},
        {"role": "Chief Finance Officer", "department": "Finance", "mission": "Guard unit economics and capital allocation."},
        {"role": "Chief Customer Officer", "department": "Customer Success", "mission": "Improve retention and feedback loops."},
        {"role": "Chief Analytics Officer", "department": "Analytics", "mission": "Monitor health, risks, and recommendations."},
    ]


def _department_plans() -> list[dict[str, Any]]:
    departments = ["Research", "Product", "Creative", "Marketing", "Sales", "Commerce & Publishing", "Finance", "Operations", "CRM", "Customer Success", "Inventory", "Procurement", "Legal", "Analytics", "Knowledge"]
    return [{"department": name, "status": "ACTIVE" if name in {"Research", "Product", "Creative", "Marketing", "Sales", "Commerce & Publishing"} else "PLANNED", "managerContract": "Mission -> Manager -> Employees -> Workflow -> Deliverables -> Validation -> Approval -> Output"} for name in departments]


def _strategic_plan(project: dict[str, Any], product_blueprint: dict[str, Any], marketing_pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "quarterlyGoals": ["Launch founder batch", "Validate demand", "Collect reviews", "Prepare optimization loop"],
        "monthlyGoals": ["Finalize approvals", "Publish drafts", "Open waitlist", "Measure first signals"],
        "weeklyGoals": marketing_pack.get("launchRoadmap", []),
        "departmentGoals": {"Product": "Validate supplier assumptions", "Marketing": "Drive qualified demand", "Sales": "Convert leads into orders", "Commerce & Publishing": "Execute approved launch actions", "Analytics": "Track launch KPIs"},
        "milestones": ["Founder approval", "First listing draft", "First campaign draft", "First customer feedback"],
        "dependencies": ["Founder approvals", "Live provider credentials", "Inventory confirmation", "Legal review for child-product claims"],
        "successMetricFocus": product_blueprint.get("profitabilityReport", {}).get("marginScore", "margin validation"),
    }


def _business_plan(product_blueprint: dict[str, Any], marketing_pack: dict[str, Any], launch_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "businessStrategy": marketing_pack.get("goToMarketStrategy"),
        "productRoadmap": product_blueprint.get("productRoadmap", []),
        "goToMarketRoadmap": marketing_pack.get("launchRoadmap", []),
        "financialRoadmap": product_blueprint.get("costAnalysis", {}),
        "growthRoadmap": ["Founder batch", "Review flywheel", "Expansion packs", "Retail/marketplace scale"],
        "riskRoadmap": launch_package.get("risks", []),
    }


def _digital_twin(project: dict[str, Any], research_report: dict[str, Any], product_blueprint: dict[str, Any], creative_pack: dict[str, Any], marketing_pack: dict[str, Any], launch_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "businessId": project["id"],
        "currentState": "PRE_LAUNCH_APPROVAL_GATED",
        "products": [{"productId": product_blueprint["productId"], "name": product_blueprint["productName"], "variants": product_blueprint.get("productVariants", [])}],
        "inventory": launch_package.get("storeManagementPlan", {}).get("inventorySync", {}),
        "customers": {"targetSegments": marketing_pack.get("customerPersonas", []), "knownCustomers": []},
        "marketing": {"strategy": marketing_pack.get("goToMarketStrategy"), "campaigns": launch_package.get("campaignLaunchPlan", {}).get("campaigns", [])},
        "sales": {"status": "READY_FOR_DEPARTMENT_PACKAGE", "channels": launch_package.get("launchReport", {}).get("channelsPrepared", [])},
        "operations": {"publishingStatus": launch_package.get("launchStatus"), "rollbackPlan": launch_package.get("rollbackPlan", {})},
        "finance": product_blueprint.get("costAnalysis", {}),
        "suppliers": product_blueprint.get("supplierRecommendations", {}),
        "goals": ["Launch safely", "Validate demand", "Protect margins", "Capture learnings"],
        "kpis": marketing_pack.get("analyticsPlan", {}).get("kpiDashboard", []),
        "evidence": [research_report.get("reportType"), product_blueprint.get("reportType"), creative_pack.get("reportType"), marketing_pack.get("reportType"), launch_package.get("reportType")],
    }


def _knowledge_graph(project: dict[str, Any], research_report: dict[str, Any], product_blueprint: dict[str, Any], creative_pack: dict[str, Any], marketing_pack: dict[str, Any], launch_package: dict[str, Any]) -> dict[str, Any]:
    nodes = [
        {"id": project["id"], "type": "business", "label": project.get("idea", "Founder business")},
        {"id": product_blueprint["productId"], "type": "product", "label": product_blueprint["productName"]},
        {"id": creative_pack["creativeId"], "type": "brand", "label": creative_pack["brandIdentity"]["brandName"]},
        {"id": marketing_pack["marketingId"], "type": "marketing", "label": "Marketing Pack"},
        {"id": launch_package["launchId"], "type": "launch", "label": "Business Launch Package"},
    ]
    edges = [
        {"from": project["id"], "to": product_blueprint["productId"], "relationship": "owns_product"},
        {"from": product_blueprint["productId"], "to": creative_pack["creativeId"], "relationship": "has_brand_assets"},
        {"from": creative_pack["creativeId"], "to": marketing_pack["marketingId"], "relationship": "feeds_marketing"},
        {"from": marketing_pack["marketingId"], "to": launch_package["launchId"], "relationship": "feeds_execution"},
        {"from": research_report["projectId"], "to": product_blueprint["productId"], "relationship": "validated_opportunity"},
    ]
    return {"businessId": project["id"], "nodes": nodes, "edges": edges, "reasoningMode": "relationship-aware deterministic graph"}


def _business_memory(project: dict[str, Any], research_report: dict[str, Any], product_blueprint: dict[str, Any], creative_pack: dict[str, Any], marketing_pack: dict[str, Any], launch_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "projects": [project["id"]],
        "products": [product_blueprint["productId"]],
        "customers": marketing_pack.get("customerPersonas", []),
        "suppliers": product_blueprint.get("supplierRecommendations", {}),
        "competitors": research_report.get("competitorAnalysis", {}),
        "campaigns": launch_package.get("campaignLaunchPlan", {}).get("campaigns", []),
        "assets": launch_package.get("assetRepository", {}).get("assets", []),
        "experiments": ["founder batch demand validation"],
        "lessonsLearned": launch_package.get("assumptions", []),
        "founderPreferences": project.get("preferences", {}),
        "historicalDecisions": [],
    }


def _portfolio_plan(project: dict[str, Any]) -> dict[str, Any]:
    return {
        "organizationId": "default-org",
        "founderId": "founder",
        "businesses": [{"businessId": project["id"], "status": "ACTIVE_PRE_LAUNCH"}],
        "sharedResources": ["supplier knowledge", "marketing learnings", "creative assets", "research evidence"],
        "capitalAllocationPolicy": "Founder approval required before reallocating capital across businesses.",
    }


def _resource_plan(project: dict[str, Any], product_blueprint: dict[str, Any], marketing_pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "budget": project.get("budget") or marketing_pack.get("marketingBudget", {}),
        "cash": "UNKNOWN_UNTIL_CONNECTED",
        "inventory": "MANUAL_CONFIRMATION_REQUIRED",
        "supplierCapacity": product_blueprint.get("supplierRecommendations", {}),
        "founderAvailability": "Strategic approvals only",
        "constraints": project.get("constraints", []),
    }


def _decision_register(launch_package: dict[str, Any], simulations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "decision": "Approve launch package for draft execution",
            "reason": "All upstream packages are present and launch actions are approval-gated.",
            "evidence": [launch_package["reportType"], "launchValidation"],
            "confidence": launch_package["launchValidation"]["score"] / 100,
            "risk": "Live publishing credentials and legal review may still be missing.",
            "alternatives": ["Hold for manual review", "Approve only non-spend drafts"],
            "expectedOutcome": "Execution-ready launch drafts without irreversible public action.",
            "approvalRequirement": "Founder approval",
        },
        {
            "decision": "Run simulation before price or budget changes",
            "reason": "Sprint 8 requires scenario analysis before recommendations.",
            "evidence": [simulation["scenario"] for simulation in simulations],
            "confidence": 0.72,
            "risk": "No live sales data yet.",
            "alternatives": ["Wait for live metrics", "Use conservative assumptions"],
            "expectedOutcome": "Better decisions with explicit assumptions.",
            "approvalRequirement": "Strategic approval",
        },
    ]


def _approval_policy(launch_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "default": "manual",
        "automatic": ["draft generation", "non-spend analysis", "knowledge capture"],
        "conditional": [{"condition": "budget <= approved cap and legal risk low", "approval": "budget approval"}],
        "manual": ["publishing", "campaign launch", "pricing change"],
        "legalApproval": ["child safety claims", "certification claims"],
        "strategicApproval": ["new product", "new supplier", "international expansion"],
        "source": launch_package.get("approvalPlan", {}),
    }


def _simulations(product_blueprint: dict[str, Any], marketing_pack: dict[str, Any]) -> list[dict[str, Any]]:
    base_price = product_blueprint.get("pricingStrategy", {}).get("retailPrice", 1299)
    if not isinstance(base_price, (int, float)):
        base_price = 1299
    return [
        {"scenario": "Increase price by 10%", "assumption": "Demand reduction below margin gain", "estimatedImpact": {"price": round(base_price * 1.1), "margin": "improves", "conversionRisk": "medium"}, "recommendation": "Test after initial demand signal"},
        {"scenario": "Double ad budget", "assumption": "Creative performance remains stable", "estimatedImpact": {"reach": "higher", "cashRisk": "higher", "approval": "budget required"}, "recommendation": "Wait for ROAS baseline"},
        {"scenario": "Add subscription expansion pack", "assumption": "Parents want recurring activities", "estimatedImpact": {"ltv": "higher", "operations": "more complex"}, "recommendation": "Validate after repeat purchase signal"},
        {"scenario": "Switch supplier", "assumption": "Alternative supplier lowers landed cost", "estimatedImpact": {"margin": "potentially higher", "qualityRisk": "requires sample validation"}, "recommendation": "Request second quote before scale"},
    ]


def _business_health(launch_package: dict[str, Any], marketing_pack: dict[str, Any], product_blueprint: dict[str, Any]) -> dict[str, Any]:
    dimensions = {
        "revenueHealth": 50,
        "profitHealth": int(product_blueprint.get("profitabilityReport", {}).get("marginScore", 76)) if isinstance(product_blueprint.get("profitabilityReport", {}).get("marginScore", 76), (int, float)) else 76,
        "marketingHealth": int(marketing_pack.get("launchReadinessScore", {}).get("score", 78)),
        "customerHealth": 55,
        "inventoryHealth": 60 if launch_package.get("storeManagementPlan", {}).get("inventorySync") else 40,
        "operationsHealth": int(launch_package.get("launchValidation", {}).get("score", 78)),
        "cashFlowHealth": 52,
    }
    return {
        "businessId": launch_package["projectId"],
        **dimensions,
        "overallBusinessHealthScore": round(mean(dimensions.values())),
        "status": "PRE_LAUNCH_ESTIMATE",
        "explanation": "Health is estimated until Sprint 7 live metrics ingestion is connected.",
    }


def _opportunities(product_blueprint: dict[str, Any], marketing_pack: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"opportunity": "Bundle Starter and Premium variants", "type": "bundle", "priority": "HIGH", "evidence": product_blueprint.get("productVariants", [])},
        {"opportunity": "Expansion activity-card pack", "type": "upsell", "priority": "MEDIUM", "evidence": marketing_pack.get("salesFunnel", {}).get("upsells", [])},
        {"opportunity": "Preschool partnership pilot", "type": "channel expansion", "priority": "MEDIUM", "evidence": marketing_pack.get("channelPrioritization", [])},
    ]


def _risks(launch_package: dict[str, Any], product_blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        *launch_package.get("risks", []),
        {"risk": "Supplier assumptions are not live-verified", "severity": "MEDIUM", "mitigation": "Connect supplier APIs or collect founder-approved quotes."},
        {"risk": "Inventory and cash data are not connected", "severity": "MEDIUM", "mitigation": "Implement Sprint 7 data ingestion before automated optimization."},
        {"risk": "Safety/legal claims need human review", "severity": "HIGH", "mitigation": "Legal approval gate remains mandatory."},
    ]


def _recommendations(health: dict[str, Any], simulations: list[dict[str, Any]], launch_package: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"recommendation": "Approve non-spend launch drafts first", "priority": "HIGH", "confidence": 0.82, "evidence": launch_package.get("launchValidation", {}), "approvalRequirement": "Founder approval"},
        {"recommendation": "Connect live metrics before budget scaling", "priority": "HIGH", "confidence": 0.78, "evidence": health, "approvalRequirement": "Strategic approval"},
        {"recommendation": "Run supplier quote comparison before inventory scale", "priority": "MEDIUM", "confidence": 0.74, "evidence": simulations[-1], "approvalRequirement": "Operations approval"},
    ]


def _learning_engine(project: dict[str, Any], launch_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "businessId": project["id"],
        "captures": ["decision outcomes", "campaign results", "supplier performance", "product performance", "failed experiments", "winning creative"],
        "initialLessons": launch_package.get("assumptions", []),
        "knowledgeUpdatePolicy": "Append-only evidence with confidence and source.",
    }


def _self_improvement_plan() -> dict[str, Any]:
    return {
        "improvable": ["department workflows", "employee prompts", "decision quality", "knowledge quality", "execution plans"],
        "protected": ["approval policy", "audit requirements", "tenant isolation", "legal restrictions"],
        "reviewCadence": "after each completed launch or material business event",
    }


def _integration_registry() -> list[dict[str, str]]:
    return [
        {"provider": "OpenAI", "status": "OPTIONAL_CONFIGURED_BY_ENV", "interface": "reasoning/image generation"},
        {"provider": "Search Providers", "status": "OPTIONAL_CONFIGURED_BY_ENV", "interface": "market evidence"},
        {"provider": "Google Drive", "status": "OPTIONAL_CONFIGURED_BY_ENV", "interface": "asset export"},
        {"provider": "Amazon/Shopify/Etsy/Meta/WhatsApp/Email", "status": "PLANNED", "interface": "approval-gated execution"},
        {"provider": "Accounting/ERP/CRM", "status": "PLANNED", "interface": "business state ingestion"},
    ]


def _dashboards() -> list[str]:
    return ["Founder Dashboard", "Executive Dashboard", "Department Dashboard", "Business Dashboard", "Portfolio Dashboard", "Financial Dashboard", "Marketing Dashboard", "Operations Dashboard", "Knowledge Dashboard", "System Dashboard"]


def _observability_plan() -> dict[str, Any]:
    return {
        "runtimeMetrics": ["workflow runtime", "department runtime", "employee runtime", "provider usage", "cost", "latency", "failures", "retries"],
        "businessMetrics": ["revenue", "margin", "CAC", "ROAS", "inventory", "customer feedback", "business health"],
        "status": "FOUNDATION_READY",
    }


def _security_plan() -> dict[str, Any]:
    return {
        "required": ["authentication", "authorization", "RBAC", "secrets management", "audit logging", "encryption", "data privacy", "approval enforcement", "tenant isolation"],
        "currentMvp": ["audit logging", "approval enforcement", "runtime secret placeholders"],
        "status": "PRODUCTION_SECURITY_NOT_COMPLETE",
    }

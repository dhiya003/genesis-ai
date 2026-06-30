"""Executable Product Department employees for Sprint 3."""

from __future__ import annotations

from typing import Any


PRODUCT_EMPLOYEES: dict[str, dict[str, Any]] = {
    "EMP-101": {
        "name": "Product Manager",
        "section": "productManagement",
        "role": "Convert research into product definition, variants, roadmap, and customer fit.",
        "inputSchema": {"required": ["project", "researchReport", "productDefinition"]},
        "outputSchema": {"required": ["productDefinition", "productFeatures", "productVariants", "productRoadmap", "customerFit"]},
        "promptContract": "Select the best product opportunity and define the product family.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-102": {
        "name": "Industrial Designer",
        "section": "engineeringSpecification",
        "role": "Define dimensions, assembly, tooling, safety, and production readiness.",
        "inputSchema": {"required": ["productDefinition"]},
        "outputSchema": {"required": ["dimensions", "assemblyMethod", "manufacturingProcess", "toolingRequirements"]},
        "promptContract": "Create a practical industrial design specification for manufacturing discussion.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-103": {
        "name": "Manufacturing Engineer",
        "section": "manufacturingPlan",
        "role": "Define manufacturing technology, process flow, yield, and risks.",
        "inputSchema": {"required": ["engineeringSpecification", "materialRecommendation"]},
        "outputSchema": {"required": ["manufacturingTechnology", "manufacturingSequence", "processFlow", "expectedYield"]},
        "promptContract": "Convert product design into a feasible manufacturing plan.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-104": {
        "name": "Material Engineer",
        "section": "materialRecommendation",
        "role": "Recommend materials and compare cost, durability, and availability.",
        "inputSchema": {"required": ["productDefinition", "constraints"]},
        "outputSchema": {"required": ["primaryMaterials", "alternativeMaterials", "materialComparison"]},
        "promptContract": "Choose practical materials that balance safety, cost, availability, and brand positioning.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-105": {
        "name": "BOM Engineer",
        "section": "bom",
        "role": "Generate complete bill of materials with costs and supplier categories.",
        "inputSchema": {"required": ["engineeringSpecification", "materialRecommendation"]},
        "outputSchema": {"required": ["items", "totalEstimatedCost"]},
        "promptContract": "Break the product into manufacturable parts and cost each part.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-106": {
        "name": "Cost Engineer",
        "section": "costAnalysis",
        "role": "Calculate landed cost, margin, break-even quantity, ROI, and pricing.",
        "inputSchema": {"required": ["bom", "packagingSpecification", "constraints"]},
        "outputSchema": {"required": ["rawMaterialCost", "landedCost", "grossMargin", "pricingStrategy"]},
        "promptContract": "Calculate realistic unit economics and recommended selling prices.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-107": {
        "name": "Packaging Engineer",
        "section": "packagingSpecification",
        "role": "Define packaging, protection, storage, sustainability, and shipping plan.",
        "inputSchema": {"required": ["engineeringSpecification", "constraints"]},
        "outputSchema": {"required": ["packagingDimensions", "packagingMaterials", "protectionStrategy", "shippingPlan"]},
        "promptContract": "Design compact, protective, supplier-ready packaging.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-108": {
        "name": "Supplier Analyst",
        "section": "supplierRecommendations",
        "role": "Produce supplier shortlist, comparison, MOQ, lead time, and risk score.",
        "inputSchema": {"required": ["bom", "materialRecommendation", "country"]},
        "outputSchema": {"required": ["shortlist", "comparison", "alternativeSuppliers"]},
        "promptContract": "Find supplier categories and shortlist assumptions for founder review.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-109": {
        "name": "Quality Engineer",
        "section": "qualityChecklist",
        "role": "Validate manufacturability, safety, packaging, customer fit, and supplier assumptions.",
        "inputSchema": {"required": ["blueprintSections"]},
        "outputSchema": {"required": ["checks", "validationReport"]},
        "promptContract": "Run quality gates and make risks explicit before founder approval.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
    "EMP-110": {
        "name": "Profitability Analyst",
        "section": "profitabilityReport",
        "role": "Calculate profit per unit, margin, scalability, inventory risk, and cash-flow impact.",
        "inputSchema": {"required": ["costAnalysis", "pricingStrategy"]},
        "outputSchema": {"required": ["profitPerUnit", "profitPercentage", "marginScore", "scalabilityScore"]},
        "promptContract": "Decide whether the product can become profitable before inventory spend.",
        "retryPolicy": {"maxAttempts": 2},
        "timeoutSeconds": 30,
    },
}


def run_product_employee(employee_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """Run a deterministic Product Department employee."""

    if employee_id not in PRODUCT_EMPLOYEES:
        raise KeyError(f"Unknown Product Department employee: {employee_id}")
    contract = PRODUCT_EMPLOYEES[employee_id]
    builders = {
        "EMP-101": _product_manager_output,
        "EMP-102": _industrial_designer_output,
        "EMP-103": _manufacturing_engineer_output,
        "EMP-104": _material_engineer_output,
        "EMP-105": _bom_engineer_output,
        "EMP-106": _cost_engineer_output,
        "EMP-107": _packaging_engineer_output,
        "EMP-108": _supplier_analyst_output,
        "EMP-109": _quality_engineer_output,
        "EMP-110": _profitability_analyst_output,
    }
    data = builders[employee_id](context)
    output = {
        "employeeId": employee_id,
        "employeeName": contract["name"],
        "department": "PRODUCT",
        "section": contract["section"],
        "status": "COMPLETED",
        "score": data.pop("score", 82),
        "confidence": data.pop("confidence", {"level": "MEDIUM", "score": 0.74}),
        "risks": data.pop("risks", []),
        "validation": data.pop("validation", _default_validation()),
        "contract": contract,
        **data,
    }
    issues = validate_product_employee_output(output)
    if issues:
        raise ValueError(f"{employee_id} output validation failed: {issues}")
    return output


def validate_product_employee_output(output: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    employee_id = output.get("employeeId")
    contract = PRODUCT_EMPLOYEES.get(str(employee_id))
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
    if not isinstance(validation, dict) or not all(validation.get(key) == "PASS" for key in ["schema", "business", "engineering", "confidence", "risk"]):
        issues.append("validation gates must all PASS")
    return issues


def _default_validation() -> dict[str, str]:
    return {"schema": "PASS", "business": "PASS", "engineering": "PASS", "confidence": "PASS", "risk": "PASS"}


def _is_wooden_toy(context: dict[str, Any]) -> bool:
    idea = str(context.get("researchReport", {}).get("idea") or context.get("project", {}).get("idea") or "").lower()
    return "wood" in idea or "toy" in idea or "children" in idea or "3-5" in idea or "3–5" in idea


def _product_name(context: dict[str, Any]) -> str:
    return context["productDefinition"]["productDefinitionDocument"]["productName"]


def _product_manager_output(context: dict[str, Any]) -> dict[str, Any]:
    definition = context["productDefinition"]["productDefinitionDocument"]
    return {
        "productDefinition": definition,
        "productFeatures": ["Core physical product", "Gift-ready packaging", "Simple instructions", "Expandable product family"],
        "productVariants": definition["variants"],
        "productRoadmap": definition["futureRoadmap"],
        "customerFit": {
            "targetCustomer": definition["targetCustomer"],
            "problemFit": "Clear",
            "purchaseTrigger": "Educational value and premium gifting appeal" if _is_wooden_toy(context) else "Identity-led gifting and validation appeal",
        },
        "score": 86,
    }


def _industrial_designer_output(context: dict[str, Any]) -> dict[str, Any]:
    toy = _is_wooden_toy(context)
    return {
        "dimensions": {"unit": "mm", "product": "30 x 30 x 30 cube", "starterSet": "6 cubes", "package": "180 x 120 x 60"} if toy else {"unit": "mm", "product": "Compact starter kit", "package": "220 x 160 x 45"},
        "materials": ["Beech wood", "Non-toxic water-based paint", "Recycled kraft board"] if toy else ["Printed paper", "Lightweight board", "Protective mailer"],
        "assemblyMethod": "Rounded wooden cubes finished, painted, inspected, packed with activity cards." if toy else "Printed components collated, inspected, and packed into starter kit.",
        "manufacturingProcess": "CNC or semi-automatic cutting, sanding, painting, drying, inspection, packaging." if toy else "Digital print, die-cut, collation, packaging.",
        "manufacturingDifficulty": "Medium" if toy else "Easy",
        "toolingRequirements": ["Cube cutting jig", "Sanding station", "Paint drying rack"] if toy else ["Digital print setup", "Die-cut template"],
        "safetyConsiderations": ["Rounded edges", "Non-toxic paint", "Choking hazard review", "Age labeling"] if toy else ["Ink safety", "Paper edge safety"],
        "estimatedProductionTime": "5-7 production days for pilot batch",
        "score": 84,
    }


def _manufacturing_engineer_output(context: dict[str, Any]) -> dict[str, Any]:
    toy = _is_wooden_toy(context)
    return {
        "manufacturingTechnology": "Small-batch woodworking with CNC-assisted cutting" if toy else "Digital print and manual kit assembly",
        "manufacturingSequence": ["Material inspection", "Cutting", "Finishing", "Decoration", "Quality inspection", "Packaging"],
        "processFlow": "Raw material -> component fabrication -> finish -> inspect -> pack -> dispatch",
        "productionAssumptions": ["Pilot MOQ 100 units", "Manual quality inspection", "Local supplier validation required"],
        "expectedYield": "92%",
        "manufacturingRisks": ["Paint curing delays", "Dimensional inconsistency", "Supplier MOQ variance"] if toy else ["Print color mismatch", "Packaging dents"],
        "score": 82,
    }


def _material_engineer_output(context: dict[str, Any]) -> dict[str, Any]:
    toy = _is_wooden_toy(context)
    primary = ["Beech wood", "Non-toxic water-based paint", "Recycled kraft board"] if toy else ["250 GSM art card", "Sticker paper", "Kraft mailer"]
    alternatives = ["Rubber wood", "Maple wood", "Bamboo composite"] if toy else ["Recycled paperboard", "Synthetic sticker stock"]
    return {
        "primaryMaterials": primary,
        "alternativeMaterials": alternatives,
        "materialComparison": [
            {"material": primary[0], "cost": "Medium", "durability": "High", "availability": "Medium", "recommendation": "Primary choice"},
            {"material": alternatives[0], "cost": "Low", "durability": "Medium", "availability": "High", "recommendation": "Backup option"},
        ],
        "costComparison": {"primarySetMaterialCost": 180 if toy else 55, "lowestCostAlternative": 150 if toy else 42, "currency": "INR"},
        "durabilityComparison": {"primary": "High", "alternative": "Medium"},
        "availabilityAssessment": "Available from Indian wooden toy and craft manufacturers; confirm lead time and certifications." if toy else "Available through local print vendors.",
        "score": 83,
    }


def _bom_engineer_output(context: dict[str, Any]) -> dict[str, Any]:
    toy = _is_wooden_toy(context)
    items = [
        {"partNumber": "LUMA-001", "component": "Beech wood cube", "quantity": 6, "material": "Beech wood", "estimatedUnitCost": 22, "supplierCategory": "Wooden component manufacturer"},
        {"partNumber": "LUMA-002", "component": "Non-toxic paint finish", "quantity": 1, "material": "Water-based paint", "estimatedUnitCost": 28, "supplierCategory": "Toy-safe coating supplier"},
        {"partNumber": "LUMA-003", "component": "Activity cards", "quantity": 12, "material": "350 GSM card", "estimatedUnitCost": 18, "supplierCategory": "Print supplier"},
        {"partNumber": "LUMA-004", "component": "Starter box", "quantity": 1, "material": "Rigid kraft board", "estimatedUnitCost": 45, "supplierCategory": "Packaging supplier"},
    ] if toy else [
        {"partNumber": "KIT-001", "component": "Printed card set", "quantity": 1, "material": "Art card", "estimatedUnitCost": 35, "supplierCategory": "Print supplier"},
        {"partNumber": "KIT-002", "component": "Sticker sheet", "quantity": 1, "material": "Sticker paper", "estimatedUnitCost": 20, "supplierCategory": "Print supplier"},
        {"partNumber": "KIT-003", "component": "Mailer box", "quantity": 1, "material": "Kraft board", "estimatedUnitCost": 28, "supplierCategory": "Packaging supplier"},
    ]
    return {"items": items, "totalEstimatedCost": sum(item["quantity"] * item["estimatedUnitCost"] for item in items), "currency": "INR", "score": 85}


def _packaging_engineer_output(context: dict[str, Any]) -> dict[str, Any]:
    toy = _is_wooden_toy(context)
    return {
        "packagingDimensions": {"unit": "mm", "length": 180 if toy else 220, "width": 120 if toy else 160, "height": 60 if toy else 45},
        "packagingMaterials": ["Rigid kraft board", "Paper pulp insert", "Tamper label"] if toy else ["Kraft mailer", "Paper sleeve"],
        "protectionStrategy": "Use fitted insert to prevent cube movement and edge damage." if toy else "Use snug mailer and paper wrap.",
        "shippingOptimization": "Under 500g target shipping slab",
        "storageOptimization": "Stackable rectangular packs, 20 units per carton",
        "sustainabilityAssessment": "Plastic-free packaging with recyclable board and paper insert",
        "shippingPlan": {"domesticCarrier": "Shiprocket or Delhivery placeholder", "targetWeightGrams": 480 if toy else 180, "damageRisk": "LOW-MEDIUM"},
        "score": 84,
    }


def _cost_engineer_output(context: dict[str, Any]) -> dict[str, Any]:
    bom_cost = context["sections"]["bom"]["totalEstimatedCost"]
    packaging_cost = 55 if _is_wooden_toy(context) else 35
    manufacturing_cost = 90 if _is_wooden_toy(context) else 45
    shipping_cost = 70 if _is_wooden_toy(context) else 45
    marketplace_fees = 130 if _is_wooden_toy(context) else 75
    taxes = 80 if _is_wooden_toy(context) else 45
    landed = bom_cost + packaging_cost + manufacturing_cost + shipping_cost + marketplace_fees + taxes
    selling = 1299 if _is_wooden_toy(context) else 699
    gross_margin = selling - landed
    return {
        "rawMaterialCost": bom_cost,
        "manufacturingCost": manufacturing_cost,
        "packagingCost": packaging_cost,
        "shippingCost": shipping_cost,
        "marketplaceFees": marketplace_fees,
        "taxes": taxes,
        "landedCost": landed,
        "grossMargin": gross_margin,
        "netMargin": gross_margin - 80,
        "breakEvenQuantity": 115,
        "roiEstimate": "1.8x on first 500 units if sell-through exceeds 70%",
        "pricingStrategy": {
            "manufacturingPrice": landed,
            "wholesalePrice": 899,
            "distributorPrice": 999,
            "retailPrice": selling,
            "marketplaceSellingPrice": selling + 100,
            "premiumPricingOption": 1799,
            "bundlePricing": 2499,
            "currency": "INR",
        },
        "score": 81,
    }


def _supplier_analyst_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "shortlist": [
            {"name": "India wooden toy manufacturer placeholder", "country": "India", "category": "Wooden toys", "moq": 100, "leadTimeDays": 21, "riskScore": 42},
            {"name": "Channapatna craft cluster placeholder", "country": "India", "category": "Wood craft", "moq": 150, "leadTimeDays": 28, "riskScore": 48},
            {"name": "Educational kit assembler placeholder", "country": "India", "category": "Assembly and packaging", "moq": 100, "leadTimeDays": 14, "riskScore": 38},
        ],
        "comparison": {"bestPilotSupplier": "Educational kit assembler placeholder", "lowestMOQ": 100, "lowestRiskScore": 38},
        "alternativeSuppliers": ["Alibaba verified wooden toy supplier", "Local CNC woodworking vendor", "Print-and-pack assembly vendor"],
        "supplierAssumptions": ["Supplier names are placeholders until live supplier research credentials are connected.", "Founder must verify certifications and samples."],
        "score": 78,
    }


def _quality_engineer_output(context: dict[str, Any]) -> dict[str, Any]:
    checks = [
        {"check": "Manufacturability", "status": "PASS"},
        {"check": "Profitability", "status": "PASS"},
        {"check": "Shipping feasibility", "status": "PASS"},
        {"check": "Packaging feasibility", "status": "PASS"},
        {"check": "Customer fit", "status": "PASS"},
        {"check": "Market differentiation", "status": "PASS"},
        {"check": "Safety assumptions", "status": "REVIEW"},
        {"check": "Supplier availability", "status": "REVIEW"},
    ]
    return {
        "checks": checks,
        "validationReport": {"passed": 6, "reviewRequired": 2, "failed": 0},
        "qualityRisks": ["Certifications must be verified before production.", "Pilot samples must pass physical inspection."],
        "score": 80,
    }


def _profitability_analyst_output(context: dict[str, Any]) -> dict[str, Any]:
    cost = context["sections"]["costAnalysis"]
    pricing = cost["pricingStrategy"]
    profit = pricing["retailPrice"] - cost["landedCost"]
    percentage = round((profit / pricing["retailPrice"]) * 100, 2)
    return {
        "profitPerUnit": profit,
        "profitPercentage": percentage,
        "marginScore": 78,
        "scalabilityScore": 74,
        "inventoryRisk": "MEDIUM",
        "cashFlowImpact": "Requires controlled pilot batch and staged reorders.",
        "profitabilityAssessment": "Commercially promising if supplier samples and safety review pass.",
        "score": 79,
    }

"""Product Department execution for Sprint 3."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

from apps.observability import MetricsRecorder
from apps.product.employees import PRODUCT_EMPLOYEES, run_product_employee
from apps.storage import JsonStore
from scripts.validate_product_blueprint import validate_product_blueprint_payload
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
    """Converts validated research into Product Definition and Product Blueprint."""

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

    def execute_blueprint(self, project: dict[str, Any], workflow: dict[str, Any], research_report: dict[str, Any]) -> dict[str, Any]:
        LOGGER.info("product blueprint started", extra={"event": "product.blueprint_started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        product_definition = self.build_product_definition(project, workflow, research_report)
        validation_issues = validate_product_definition_payload(product_definition)
        if validation_issues:
            raise ValueError(f"Product definition validation failed: {validation_issues}")
        self.store.save_product_definition(product_definition)

        context: dict[str, Any] = {
            "project": project,
            "workflow": workflow,
            "researchReport": research_report,
            "productDefinition": product_definition,
            "sections": {},
        }
        employee_outputs: list[dict[str, Any]] = []
        for employee_id in PRODUCT_EMPLOYEES:
            started = perf_counter()
            output = run_product_employee(employee_id, context)
            output["projectId"] = project["id"]
            output["workflowId"] = workflow["id"]
            self.store.save_employee_output(output)
            context["sections"][output["section"]] = output
            employee_outputs.append(output)
            MetricsRecorder(self.store).record(
                "product.employee_completed",
                {"employeeId": employee_id, "runtimeSeconds": round(perf_counter() - started, 4), "score": output.get("score")},
                project_id=project["id"],
                workflow_id=workflow["id"],
            )

        blueprint = self.build_product_blueprint(project, workflow, research_report, product_definition, employee_outputs)
        blueprint_issues = validate_product_blueprint_payload(blueprint)
        if blueprint_issues:
            raise ValueError(f"Product blueprint validation failed: {blueprint_issues}")

        self.store.save_product_blueprint(blueprint)
        self.store.save_bom_report(project["id"], blueprint["bom"])
        self.store.save_cost_report(project["id"], blueprint["costAnalysis"])
        self.store.save_supplier_report(project["id"], blueprint["supplierRecommendations"])
        self.store.save_packaging_report(project["id"], blueprint["packagingSpecification"])
        self.store.save_profitability_report(project["id"], blueprint["profitabilityReport"])
        self.store.save_manufacturing_plan(project["id"], blueprint["manufacturingPlan"])
        for entry in blueprint["knowledgeBaseEntries"]:
            self.store.save_product_knowledge(entry)

        MetricsRecorder(self.store).record(
            "product.blueprint_stored",
            {
                "overallScore": blueprint["overallScore"],
                "employeeCount": len(employee_outputs),
                "landedCost": blueprint["costAnalysis"]["landedCost"],
            },
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("product blueprint stored", extra={"event": "product.blueprint_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return blueprint

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
        product_strategy = {
            "strategyOwner": "EMP-101 Product Manager",
            "targetCustomer": target_customer,
            "customerProblem": product_definition_document["problemSolved"],
            "valueProposition": product_definition_document["purpose"],
            "positioning": "Premium, practical, pilot-ready product family with clear customer benefit.",
            "differentiation": product_definition_document["differentiator"],
            "competitiveAdvantage": "Lower validation risk through compact variants, explicit constraints, and supplier-ready planning.",
            "pricingPhilosophy": "Protect gross margin first, then use bundles and premium variants to lift average order value.",
            "roadmap": roadmap,
            "variantStrategy": variants,
            "researchReferences": [citation.get("url") or citation.get("source") for citation in research_report.get("citations", [])],
        }
        product_specification = {
            "productName": product_name,
            "description": product_definition_document["productStory"],
            "features": ["Core physical product", "Gift-ready packaging", "Simple instructions", "Expandable variant system"],
            "dimensions": "Defined by Industrial Designer during Product Blueprint generation",
            "weight": "Target under 500g for starter variant",
            "materials": [product_definition_document["recommendedMaterial"]],
            "targetCustomer": target_customer,
            "functionalRequirements": ["Easy to understand", "Easy to package", "Easy to ship", "Supplier-discussion ready"],
            "nonFunctionalRequirements": ["Safe assumptions explicit", "Low MOQ friendly", "Brandable", "Auditable"],
            "variants": variants,
            "version": "1.0",
            "traceability": {"sourceReportId": research_report["projectId"], "sourceWorkflowId": research_report["workflowId"]},
        }
        product_architecture = {
            "coreProduct": product_name,
            "components": ["Primary product", "Instruction layer", "Packaging", "Brand insert"],
            "variantArchitecture": [variant["level"] for variant in variants],
            "dependencies": ["Supplier sample", "Packaging dieline", "Safety review"],
            "versioningModel": "Starter validates core architecture; Standard and Premium expand contents and packaging.",
        }
        product_concept_validation = {
            "customerValue": "PASS",
            "manufacturability": "PASS_WITH_BLUEPRINT_DETAIL",
            "shippingFit": "PASS",
            "brandability": "PASS",
            "scalability": "PASS",
            "reviewItems": ["Confirm supplier quotes", "Validate customer willingness to pay", "Review category safety rules"],
            "decision": "APPROVED_FOR_PRODUCT_BLUEPRINT",
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
            "departmentStatus": "INITIALIZED",
            "departmentInitialization": {
                "status": "READY",
                "entryCriteria": ["Validated Research Report", "Founder idea", "Project context"],
                "workflow": ["Product strategy", "Product specification", "Variants", "Architecture", "Concept validation"],
                "output": "Product Definition Document",
            },
            "productManager": {
                "employeeId": "EMP-101",
                "name": "Product Manager",
                "assignmentStatus": "ASSIGNED",
                "responsibilities": ["Read research report", "Select opportunity", "Create product plan", "Prepare blueprint handoff"],
            },
            "productExecutionPlan": {
                "steps": ["Read research report", "Rank opportunity", "Define product", "Design variants", "Validate concept"],
                "automation": "FULLY_AUTOMATED",
                "manualDependencies": [],
            },
            "dashboardUpdate": {"status": "PRODUCT_DEFINITION_COMPLETED", "visibleToFounder": True},
            "auditSummary": {"createdBy": "ProductDepartment", "sourceReportId": research_report["projectId"], "workflowId": workflow["id"]},
            "productDefinitionDocument": product_definition_document,
            "productStrategy": product_strategy,
            "productSpecification": product_specification,
            "productArchitecture": product_architecture,
            "productConceptValidation": product_concept_validation,
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

    def build_product_blueprint(
        self,
        project: dict[str, Any],
        workflow: dict[str, Any],
        research_report: dict[str, Any],
        product_definition: dict[str, Any],
        employee_outputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sections = {output["section"]: output for output in employee_outputs}
        cost_analysis = sections["costAnalysis"]
        pricing_strategy = cost_analysis["pricingStrategy"]
        profitability = sections["profitabilityReport"]
        quality = sections["qualityChecklist"]
        product_name = product_definition["productDefinitionDocument"]["productName"]
        review_gate = _product_review_gate(product_definition, sections)
        validation_history = [
            {"stage": "Product Definition", "status": "PASS", "validator": "validate_product_definition.py"},
            {"stage": "Employee Outputs", "status": "PASS", "validator": "validate_product_employee_output"},
            {"stage": "Product Blueprint", "status": "PASS", "validator": "validate_product_blueprint.py"},
        ]
        return {
            "reportType": "PRODUCT_BLUEPRINT",
            "version": "0.3.0",
            "projectId": project["id"],
            "productId": project["id"],
            "workflowId": workflow["id"],
            "sourceReportId": research_report["projectId"],
            "sourceWorkflowId": research_report["workflowId"],
            "sourceIdea": research_report["idea"],
            "department": "PRODUCT",
            "departmentStatus": "COMPLETED",
            "productName": product_name,
            "executiveSummary": f"Genesis Product Department generated a manufacturable, costed Product Blueprint for {product_name}.",
            "departmentInitialization": product_definition["departmentInitialization"],
            "productManager": product_definition["productManager"],
            "productExecutionPlan": {
                "steps": ["Product management", "Industrial design", "Manufacturing", "Materials", "BOM", "Costing", "Packaging", "Supplier analysis", "Quality", "Profitability"],
                "employees": list(PRODUCT_EMPLOYEES.keys()),
                "automation": "FULLY_AUTOMATED",
            },
            "productStrategy": product_definition["productStrategy"],
            "productSpecification": product_definition["productSpecification"],
            "productDefinition": sections["productManagement"]["productDefinition"],
            "productFeatures": sections["productManagement"]["productFeatures"],
            "productVariants": sections["productManagement"]["productVariants"],
            "productRoadmap": sections["productManagement"]["productRoadmap"],
            "customerFit": sections["productManagement"]["customerFit"],
            "productConstraints": product_definition["constraintsReport"],
            "productSuccessMetrics": product_definition["successMetrics"],
            "productArchitecture": product_definition["productArchitecture"],
            "productConceptValidation": product_definition["productConceptValidation"],
            "engineeringSpecification": {
                "dimensions": sections["engineeringSpecification"]["dimensions"],
                "materials": sections["engineeringSpecification"]["materials"],
                "assemblyMethod": sections["engineeringSpecification"]["assemblyMethod"],
                "manufacturingProcess": sections["engineeringSpecification"]["manufacturingProcess"],
                "manufacturingDifficulty": sections["engineeringSpecification"]["manufacturingDifficulty"],
                "toolingRequirements": sections["engineeringSpecification"]["toolingRequirements"],
                "safetyConsiderations": sections["engineeringSpecification"]["safetyConsiderations"],
                "estimatedProductionTime": sections["engineeringSpecification"]["estimatedProductionTime"],
            },
            "materialRecommendation": {
                "primaryMaterials": sections["materialRecommendation"]["primaryMaterials"],
                "alternativeMaterials": sections["materialRecommendation"]["alternativeMaterials"],
                "materialComparison": sections["materialRecommendation"]["materialComparison"],
                "costComparison": sections["materialRecommendation"]["costComparison"],
                "durabilityComparison": sections["materialRecommendation"]["durabilityComparison"],
                "availabilityAssessment": sections["materialRecommendation"]["availabilityAssessment"],
            },
            "materialRecommendations": sections["materialRecommendation"],
            "manufacturabilityEvaluation": {
                "score": sections["engineeringSpecification"]["score"],
                "manufacturingDifficulty": sections["engineeringSpecification"]["manufacturingDifficulty"],
                "toolingRequirements": sections["engineeringSpecification"]["toolingRequirements"],
                "decision": "MANUFACTURABLE_FOR_PILOT",
            },
            "manufacturingPlan": {
                "manufacturingTechnology": sections["manufacturingPlan"]["manufacturingTechnology"],
                "manufacturingSequence": sections["manufacturingPlan"]["manufacturingSequence"],
                "processFlow": sections["manufacturingPlan"]["processFlow"],
                "productionAssumptions": sections["manufacturingPlan"]["productionAssumptions"],
                "expectedYield": sections["manufacturingPlan"]["expectedYield"],
                "manufacturingRisks": sections["manufacturingPlan"]["manufacturingRisks"],
            },
            "manufacturingMethodSelection": {
                "selectedMethod": sections["manufacturingPlan"]["manufacturingTechnology"],
                "sequence": sections["manufacturingPlan"]["manufacturingSequence"],
                "rationale": "Chosen for pilot feasibility, low tooling risk, and supplier availability.",
                "risks": sections["manufacturingPlan"]["manufacturingRisks"],
            },
            "bom": sections["bom"],
            "costAnalysis": cost_analysis,
            "pricingStrategy": pricing_strategy,
            "packagingSpecification": {
                "packagingDimensions": sections["packagingSpecification"]["packagingDimensions"],
                "primaryPackaging": sections["packagingSpecification"]["primaryPackaging"],
                "secondaryPackaging": sections["packagingSpecification"]["secondaryPackaging"],
                "protectiveInserts": sections["packagingSpecification"]["protectiveInserts"],
                "packagingMaterials": sections["packagingSpecification"]["packagingMaterials"],
                "labels": sections["packagingSpecification"]["labels"],
                "barcodes": sections["packagingSpecification"]["barcodes"],
                "qrCodes": sections["packagingSpecification"]["qrCodes"],
                "protectionStrategy": sections["packagingSpecification"]["protectionStrategy"],
                "shippingOptimization": sections["packagingSpecification"]["shippingOptimization"],
                "storageOptimization": sections["packagingSpecification"]["storageOptimization"],
                "storageRequirements": sections["packagingSpecification"]["storageRequirements"],
                "brandingRequirements": sections["packagingSpecification"]["brandingRequirements"],
                "estimatedPackagingCost": sections["packagingSpecification"]["estimatedPackagingCost"],
                "sustainabilityAssessment": sections["packagingSpecification"]["sustainabilityAssessment"],
            },
            "shippingPlan": sections["packagingSpecification"]["shippingPlan"],
            "shippingAssessment": sections["packagingSpecification"]["shippingPlan"],
            "supplierRecommendations": sections["supplierRecommendations"],
            "qualityChecklist": quality["checks"],
            "qualityAssessment": quality,
            "validationReport": quality["validationReport"],
            "blueprintValidationReport": {
                "status": "PASS",
                "schemaValidation": "PASS",
                "businessValidation": "PASS",
                "engineeringValidation": "PASS",
                "qualityGate": quality["validationReport"],
                "validationHistory": validation_history,
            },
            "validationHistory": validation_history,
            "profitabilityReport": profitability,
            "profitabilityAnalysis": profitability,
            "risks": _blueprint_risks(research_report, sections),
            "assumptions": _blueprint_assumptions(sections),
            "recommendations": [
                "Request physical samples from two shortlisted suppliers before placing a production order.",
                "Run a 100-unit pilot batch before scaling inventory.",
                "Verify safety labeling, paint compliance, and age suitability before launch.",
            ],
            "nextActions": [
                "Send the BOM and engineering specification to shortlisted suppliers.",
                "Collect quotes for 100, 250, and 500 unit production runs.",
                "Approve packaging dieline and pilot sample quality checklist.",
            ],
            "launchReadyEngineeringPackage": {
                "included": ["Product definition", "Engineering specification", "Manufacturing plan", "BOM", "Packaging specification", "Supplier shortlist", "Cost and pricing analysis", "Quality checklist"],
                "readyForSupplierDiscussion": True,
                "requiresHumanReviewBeforeProduction": ["Supplier verification", "Safety certification", "Physical sample approval"],
            },
            "productReviewGate": review_gate,
            "completionChecklist": _blueprint_completion_checklist(),
            "creativeStudioTransition": {
                "status": "READY",
                "approvedForCreativeStudio": review_gate["approvedForCreativeStudio"],
                "handoffArtifacts": ["Product Blueprint", "Product variants", "Packaging specification", "Brandable product story"],
            },
            "founderNotification": {
                "status": "READY_FOR_REVIEW",
                "message": "Product Blueprint is complete and ready for founder review before Creative Studio execution.",
            },
            "departmentMetrics": {
                "employeeCount": len(employee_outputs),
                "overallScore": round(mean(output["score"] for output in employee_outputs)),
                "qualityReviewItems": quality["validationReport"]["reviewRequired"],
            },
            "auditSummary": {"createdBy": "ProductDepartment", "workflowId": workflow["id"], "sourceReportId": research_report["projectId"]},
            "employeeOutputs": employee_outputs,
            "knowledgeBaseEntries": _knowledge_entries(project, product_name, product_definition["opportunityReport"]["rejectedAlternatives"]),
            "overallScore": round(mean(output["score"] for output in employee_outputs)),
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
    if "toy" in idea.lower() or "children" in idea.lower() or "kids" in idea.lower():
        return "Help children aged 3-5 build logic, motor skills, and pattern recognition through a premium wooden play experience."
    if "coffee" in idea.lower():
        return "Help coffee lovers express their identity through an affordable, giftable starter kit."
    return f"Convert the validated market opportunity into a simple, manufacturable {base_product}."


def _target_customer(research_report: dict[str, Any]) -> dict[str, Any]:
    idea = str(research_report.get("idea", "")).lower()
    if "toy" in idea or "children" in idea or "kids" in idea:
        return {
            "primarySegment": "Parents of children aged 3-5 in India",
            "buyer": "Parents and gift buyers",
            "user": "Children aged 3-5",
            "ageGroup": "3-5",
            "needs": [
                "Safe educational play",
                "Premium durable materials",
                "Simple learning activities",
            ],
        }
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


def _blueprint_risks(research_report: dict[str, Any], sections: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    source_risks = research_report.get("risks", [])
    risks = [
        {"risk": _first_text(source_risks[:1], "Demand may not convert into purchases."), "severity": "HIGH", "mitigation": "Validate with pilot orders before production scale."},
        {"risk": "Supplier shortlist uses deterministic placeholders until live supplier credentials are connected.", "severity": "MEDIUM", "mitigation": "Verify suppliers, samples, certifications, and quotes manually."},
        {"risk": "Safety compliance assumptions require expert review before manufacturing.", "severity": "HIGH", "mitigation": "Confirm toy safety, paint, labeling, and choking hazard requirements."},
    ]
    for risk in sections.get("qualityChecklist", {}).get("qualityRisks", []):
        risks.append({"risk": risk, "severity": "MEDIUM", "mitigation": "Resolve during pilot sample review."})
    return risks


def _blueprint_assumptions(sections: dict[str, dict[str, Any]]) -> list[str]:
    assumptions = [
        "All costs are deterministic planning estimates until supplier quotes are collected.",
        "Supplier names are placeholders unless live supplier research credentials are configured.",
        "Final product safety must be reviewed before manufacturing.",
    ]
    assumptions.extend(sections.get("supplierRecommendations", {}).get("supplierAssumptions", []))
    assumptions.extend(sections.get("manufacturingPlan", {}).get("productionAssumptions", []))
    return assumptions


def _product_review_gate(product_definition: dict[str, Any], sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    quality = sections.get("qualityChecklist", {})
    profitability = sections.get("profitabilityReport", {})
    return {
        "gateName": "Product Review Gate",
        "status": "APPROVED_WITH_REVIEW_ITEMS",
        "approvedForCreativeStudio": True,
        "founderApprovalRequiredBeforeProduction": True,
        "criteria": [
            {"name": "Validated product definition", "status": "PASS"},
            {"name": "Starter, Standard, Premium variants", "status": "PASS"},
            {"name": "Manufacturing feasibility", "status": "PASS"},
            {"name": "Positive unit economics", "status": "PASS" if profitability.get("profitPerUnit", 0) > 0 else "FAIL"},
            {"name": "Quality and safety assumptions explicit", "status": "REVIEW"},
        ],
        "reviewItems": quality.get("qualityRisks", []),
        "nextDepartment": "CREATIVE",
        "sourceProductDefinition": product_definition["projectId"],
    }


def _blueprint_completion_checklist() -> list[dict[str, str]]:
    return [
        {"item": "Product Definition", "status": "COMPLETED"},
        {"item": "Engineering Specification", "status": "COMPLETED"},
        {"item": "Material Recommendation", "status": "COMPLETED"},
        {"item": "Manufacturing Plan", "status": "COMPLETED"},
        {"item": "BOM", "status": "COMPLETED"},
        {"item": "Cost and Pricing", "status": "COMPLETED"},
        {"item": "Packaging and Shipping", "status": "COMPLETED"},
        {"item": "Supplier Intelligence", "status": "COMPLETED"},
        {"item": "Quality Validation", "status": "COMPLETED_WITH_REVIEW_ITEMS"},
        {"item": "Profitability", "status": "COMPLETED"},
        {"item": "Creative Studio Handoff", "status": "READY"},
    ]

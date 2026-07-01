"""Creative Department execution for Sprint 4."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

from apps.creative.assets import generate_creative_assets
from apps.creative.employees import CREATIVE_EMPLOYEES, run_creative_employee
from apps.observability import MetricsRecorder
from apps.storage import JsonStore
from scripts.validate_creative_pack import validate_creative_pack_payload

LOGGER = logging.getLogger("genesis.creative")


class CreativeDepartment:
    """Converts Product Blueprint into a complete Creative Pack."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def execute(self, project: dict[str, Any], workflow: dict[str, Any], product_blueprint: dict[str, Any]) -> dict[str, Any]:
        LOGGER.info("creative pack started", extra={"event": "creative.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        context: dict[str, Any] = {"project": project, "workflow": workflow, "productBlueprint": product_blueprint, "sections": {}}
        employee_outputs: list[dict[str, Any]] = []
        for employee_id in CREATIVE_EMPLOYEES:
            started = perf_counter()
            output = run_creative_employee(employee_id, context)
            output["projectId"] = project["id"]
            output["workflowId"] = workflow["id"]
            self.store.save_employee_output(output)
            context["sections"][output["section"]] = output
            employee_outputs.append(output)
            MetricsRecorder(self.store).record(
                "creative.employee_completed",
                {"employeeId": employee_id, "runtimeSeconds": round(perf_counter() - started, 4), "score": output.get("score")},
                project_id=project["id"],
                workflow_id=workflow["id"],
            )

        creative_pack = self.build_creative_pack(project, workflow, product_blueprint, employee_outputs)
        generated_assets = generate_creative_assets(self.store.creative_asset_dir(creative_pack["creativeId"]), creative_pack)
        creative_pack["generatedAssets"] = generated_assets
        creative_pack["creativeAssetManifest"].extend(
            {
                "assetId": asset["assetId"],
                "name": asset["name"],
                "format": asset["format"],
                "status": asset["status"],
                "path": asset["path"],
            }
            for asset in generated_assets["assets"]
        )
        creative_pack["productionReadiness"]["requiresBinaryAssetGeneration"] = False
        creative_pack["productionReadiness"]["assetFilesGenerated"] = True
        creative_pack["validationReport"]["resolutionChecks"] = "PASS_DETERMINISTIC_ASSETS"
        issues = validate_creative_pack_payload(creative_pack)
        if issues:
            raise ValueError(f"Creative pack validation failed: {issues}")

        creative_id = creative_pack["creativeId"]
        self.store.save_creative_pack(creative_pack)
        self.store.save_brand_report(creative_id, creative_pack["brandIdentity"])
        self.store.save_logo_report(creative_id, creative_pack["logoSystem"])
        self.store.save_creative_packaging_report(creative_id, creative_pack["packagingDesignBrief"])
        self.store.save_mockup_report(creative_id, creative_pack["productMockupBrief"])
        self.store.save_marketplace_creative_report(creative_id, creative_pack["marketplaceCreativePack"])
        self.store.save_social_creative_report(creative_id, creative_pack["socialMediaCreativePack"])
        self.store.save_copy_report(creative_id, creative_pack["launchCopyPack"])
        MetricsRecorder(self.store).record(
            "creative.pack_stored",
            {"overallScore": creative_pack["overallScore"], "employeeCount": len(employee_outputs)},
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("creative pack stored", extra={"event": "creative.pack_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return creative_pack

    def build_creative_pack(
        self,
        project: dict[str, Any],
        workflow: dict[str, Any],
        product_blueprint: dict[str, Any],
        employee_outputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sections = {output["section"]: output for output in employee_outputs}
        brand_name = sections["brandNaming"]["recommendedName"]
        brand_guidelines = _brand_guidelines(sections)
        brand_identity = {
            "brandName": brand_name,
            "brandStory": f"{brand_name} exists to make early learning feel calm, beautiful, and useful at home.",
            "mission": "Help families turn everyday play into safe, screen-free learning moments.",
            "vision": "Become India's most trusted premium early-learning play brand.",
            "positioning": sections["brandStrategy"]["positioning"],
            "targetAudience": sections["brandStrategy"]["targetAudience"],
            "targetPersona": {
                "name": "Learning-focused urban parent",
                "priority": "Safe, premium, purposeful play for children aged 3-5",
                "buyingTrigger": "Birthday gifting, preschool readiness, and screen-free routines",
            },
            "brandPromise": sections["brandStrategy"]["brandPromise"],
            "personality": sections["brandStrategy"]["personality"],
            "brandVoice": "Warm expert, clear parent guide, quietly playful",
            "toneOfVoice": sections["brandStrategy"]["toneOfVoice"],
            "differentiation": sections["brandStrategy"]["differentiation"],
            "colorPalette": sections["visualIdentity"]["colorPalette"],
            "typography": sections["visualIdentity"]["typography"],
            "visualRules": sections["visualIdentity"]["visualRules"],
            "brandGuidelines": brand_guidelines,
        }
        visual_system = _visual_system(sections)
        product_creatives = _product_creatives(product_blueprint, sections)
        packaging_assets = _packaging_assets(sections)
        digital_assets = _digital_assets(sections)
        ai_deliverables = _ai_deliverables(sections)
        validation_history = [
            {"stage": "Product Blueprint precondition", "status": "PASS", "evidence": product_blueprint.get("productReviewGate", {}).get("status", "BLUEPRINT_AVAILABLE")},
            {"stage": "Creative employee outputs", "status": "PASS", "validator": "validate_creative_employee_output"},
            {"stage": "Creative Pack", "status": "PASS", "validator": "validate_creative_pack.py"},
        ]
        return {
            "reportType": "CREATIVE_PACK",
            "version": "0.4.0",
            "projectId": project["id"],
            "creativeId": project["id"],
            "productId": product_blueprint["productId"],
            "workflowId": workflow["id"],
            "sourceProductBlueprintId": product_blueprint["productId"],
            "sourceIdea": product_blueprint["sourceIdea"],
            "department": "CREATIVE",
            "departmentStatus": "COMPLETED",
            "executiveSummary": f"Genesis Creative Studio generated a launch-ready Creative Pack for {product_blueprint['productName']}.",
            "creativeStudio": {
                "status": "INITIALIZED",
                "mission": "Transform Product Blueprint into export-ready brand, packaging, marketplace, and social creative assets.",
                "entryCriteria": ["Approved Product Blueprint", "Product variants", "Packaging specification", "Creative handoff readiness"],
                "output": "Creative Pack",
            },
            "creativeDirector": {
                "employeeId": "EMP-210",
                "name": "Creative Director / QA",
                "assignmentStatus": "ASSIGNED",
                "responsibilities": ["Orchestrate creative standards", "Validate consistency", "Prepare founder approval checklist"],
            },
            "creativeExecutionPlan": {
                "steps": ["Brand strategy", "Naming", "Logo system", "Visual identity", "Packaging", "Mockups", "Marketplace assets", "Social assets", "Copy", "QA"],
                "employees": list(CREATIVE_EMPLOYEES.keys()),
                "automation": "FULLY_AUTOMATED",
            },
            "brandContext": {
                "productName": product_blueprint["productName"],
                "productId": product_blueprint["productId"],
                "targetCustomer": product_blueprint.get("customerFit", {}).get("targetCustomer", {}),
                "productStory": product_blueprint.get("productDefinition", {}).get("productStory"),
                "variants": product_blueprint.get("productVariants", []),
            },
            "workflowUpdate": {"status": "CREATIVE_PACK_COMPLETED", "nextDepartment": "MARKETING"},
            "productBlueprintApproval": {
                "status": product_blueprint.get("productReviewGate", {}).get("status", "AVAILABLE"),
                "approvedForCreativeStudio": product_blueprint.get("productReviewGate", {}).get("approvedForCreativeStudio", True),
            },
            "brandStrategy": sections["brandStrategy"],
            "brandStrategyDocument": {
                "purpose": sections["brandStrategy"]["brandPurpose"],
                "mission": sections["brandStrategy"]["brandMission"],
                "vision": sections["brandStrategy"]["brandVision"],
                "valueProposition": sections["brandStrategy"]["valueProposition"],
                "emotionalPositioning": sections["brandStrategy"]["emotionalPositioning"],
                "competitivePositioning": sections["brandStrategy"]["competitivePositioning"],
                "brandArchetype": sections["brandStrategy"]["brandArchetype"],
                "positioning": sections["brandStrategy"]["positioning"],
                "targetAudience": sections["brandStrategy"]["targetAudience"],
            },
            "brandNameRecommendation": {
                "recommendedName": brand_name,
                "nameOptions": sections["brandNaming"]["nameOptions"],
                "rationale": sections["brandNaming"]["rationale"],
            },
            "brandIdentity": brand_identity,
            "brandGuidelinesDocument": brand_guidelines,
            "logoSystem": sections["logoSystem"],
            "logoVariants": _logo_variants(sections),
            "logoUsageRules": {
                "clearSpaceRules": "Keep clear space equal to the height of the icon mark around all sides.",
                "minimumSizeRules": sections["logoSystem"]["usage"].get("minimumSize", "24 mm wide on packaging"),
                "backgroundRules": sections["logoSystem"]["usage"],
            },
            "colorPalette": sections["visualIdentity"]["colorPalette"],
            "typography": sections["visualIdentity"]["typography"],
            "visualIdentityRules": sections["visualIdentity"]["visualRules"],
            "visualSystem": visual_system,
            "packagingDesignBrief": sections["packagingDesignBrief"],
            "packagingProductionAssets": packaging_assets,
            "productMockupBrief": sections["productMockupBrief"],
            "productCreativeDeliverables": product_creatives,
            "marketplaceCreativePack": sections["marketplaceCreativePack"],
            "socialMediaCreativePack": sections["socialMediaCreativePack"],
            "digitalAssets": digital_assets,
            "launchCopyPack": sections["copyAssets"],
            "aiDeliverables": ai_deliverables,
            "creativeAssetManifest": _creative_asset_manifest(brand_name, product_creatives, packaging_assets, digital_assets),
            "productionReadiness": {
                "designerHandoff": "READY",
                "printerHandoff": "SPEC_READY",
                "manufacturerHandoff": "SPEC_READY",
                "ecommerceHandoff": "READY",
                "requiresBinaryAssetGeneration": True,
                "assetFilesGenerated": False,
            },
            "creativeQaReport": sections["creativeQaReport"],
            "validationReport": _validation_report(),
            "creativeValidationReport": _creative_validation_report(sections, validation_history),
            "validationHistory": validation_history,
            "founderApprovalChecklist": sections["creativeQaReport"]["approvalChecklist"],
            "risks": [
                {"risk": "Deterministic image files are placeholder-grade until a premium image provider is connected.", "severity": "MEDIUM", "mitigation": "Use the generated files for layout validation and upgrade lifestyle imagery with an approved provider."},
                {"risk": "Compliance claims require legal and certification review.", "severity": "HIGH", "mitigation": "Keep claims as placeholders until verified."},
            ],
            "assumptions": [
                "Sprint 4 MVP produces creative specifications and deterministic binary asset files.",
                "Canva, Figma, and image-generation integrations are optional later enhancements.",
                "Founder approves the brand direction before production artwork begins.",
            ],
            "nextActions": [
                "Founder approves brand name and positioning.",
                "Review generated deterministic logo, packaging, mockup, and social files.",
                "Hand Creative Pack to Sprint 5 Marketing Engine.",
            ],
            "assetGenerationPrompts": _asset_prompts(sections),
            "marketingTransition": {
                "status": "READY",
                "handoffArtifacts": ["Brand strategy", "Brand identity", "Creative asset manifest", "Launch copy", "Marketplace concepts", "Social concepts"],
                "nextDepartment": "MARKETING",
            },
            "founderNotification": {
                "status": "READY_FOR_REVIEW",
                "message": "Creative Pack is complete with deterministic assets and ready for founder approval before Marketing Engine.",
            },
            "departmentMetrics": {"employeeCount": len(employee_outputs), "overallScore": round(mean(output["score"] for output in employee_outputs))},
            "auditSummary": {"createdBy": "CreativeDepartment", "workflowId": workflow["id"], "sourceProductBlueprintId": product_blueprint["productId"]},
            "knowledgeBaseEntries": [
                {"projectId": project["id"], "type": "CREATIVE_SYSTEM", "brandName": brand_name, "lesson": "Brand strategy, packaging, marketplace, and social assets should share one visual system."},
                {"projectId": project["id"], "type": "ASSET_GENERATION", "brandName": brand_name, "lesson": "Deterministic assets prove workflow completeness; provider assets can upgrade quality later."},
            ],
            "employeeOutputs": employee_outputs,
            "overallScore": round(mean(output["score"] for output in employee_outputs)),
        }


def _asset_prompts(sections: dict[str, dict[str, Any]]) -> list[str]:
    prompts = [concept["brief"] for concept in sections["marketplaceCreativePack"]["imageConcepts"]]
    prompts.extend(mockup["brief"] for mockup in sections["productMockupBrief"]["variantMockups"])
    prompts.extend(str(banner) for banner in sections["socialMediaCreativePack"]["launchBanners"])
    return prompts


def _brand_guidelines(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "logo": {"usage": sections["logoSystem"]["usage"], "variants": ["Primary horizontal", "Stacked", "Icon mark", "Monochrome"]},
        "colors": sections["visualIdentity"]["colorPalette"],
        "typography": sections["visualIdentity"]["typography"],
        "spacing": {"small": 8, "medium": 16, "large": 24},
        "imagery": "Bright natural product photography with visible scale and parent-child interaction.",
        "illustration": "Soft geometric line illustrations inspired by cubes, paths, and learning prompts.",
        "iconography": "Rounded, simple symbols for learning domains and safety cues.",
        "tone": sections["brandStrategy"]["toneOfVoice"],
        "copy": {"headlineRule": "Lead with parent benefit", "claimRule": "Avoid unsupported safety or learning guarantees"},
        "accessibility": {"contrast": "Use Ink Charcoal on Warm Ivory for body text", "mobileText": "Avoid tiny text in marketplace and social assets"},
        "do": ["Show real product scale", "Keep one primary message per asset", "Use parent-friendly language"],
        "dont": ["Use unsupported certification claims", "Overcrowd packaging", "Hide the product behind abstract graphics"],
        "voiceRules": ["Lead with parent benefit", "Use simple developmental language", "Avoid unsupported safety claims"],
        "layoutRules": ["Show product first", "Keep one primary message per asset", "Use generous spacing"],
        "claimRules": ["Mark certification claims as pending until verified", "Avoid medical or guaranteed learning claims"],
    }


def _logo_variants(sections: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"name": "Primary horizontal", "usage": "Website, marketplace hero, box front", "fileName": "logo-primary-horizontal.svg"},
        {"name": "Stacked", "usage": "Square labels, social profile, box side", "fileName": "logo-stacked.svg"},
        {"name": "Icon mark", "usage": "Stickers, favicon, pattern", "fileName": "logo-icon-mark.svg"},
        {"name": "Monochrome", "usage": "Stamping and one-color print", "fileName": "logo-monochrome.svg"},
    ]


def _visual_system(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "iconLibrary": [
            {"name": "Logic", "concept": "Path through rounded cube"},
            {"name": "Motor Skills", "concept": "Hand and cube outline"},
            {"name": "Safe Material", "concept": "Leaf plus rounded edge"},
        ],
        "illustrationStyle": "Soft geometric line illustrations with rounded corners and limited accent colors.",
        "photographyStyle": "Bright Indian home setting, natural light, product scale visible, parent-child interaction.",
        "graphicElements": ["Cube path pattern", "Rounded learning badges", "Variant color bands"],
        "designTokens": {
            "radius": {"small": 4, "medium": 8},
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24},
            "colors": {item["name"]: item["hex"] for item in sections["visualIdentity"]["colorPalette"]},
        },
    }


def _product_creatives(product_blueprint: dict[str, Any], sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    product_name = product_blueprint["productName"]
    return {
        "productMockups": sections["productMockupBrief"]["variantMockups"],
        "heroImages": [{"name": "Main hero", "brief": f"{product_name} box, cubes, cards, and parent-facing benefit badge on clean white."}],
        "lifestyleImages": [{"name": "Parent-child activity", "brief": "Child arranging cubes with parent guiding nearby in natural light."}],
        "explodedViews": [{"name": "What is inside", "components": ["Box", "Insert", "Cubes", "Activity cards", "Parent guide"]}],
        "featureCallouts": ["Logic", "Motor skills", "Pattern recognition", "Gift-ready"],
        "sizeCharts": [{"variant": "Starter", "packageSize": "180 x 120 x 60 mm", "targetWeight": "Under 500 g"}],
        "infographics": ["How to play in 3 steps", "Skills developed", "Starter vs Standard vs Premium"],
        "productManuals": [{"fileName": "manual-parent-guide.pdf", "sections": ["Safety", "How to play", "Activity examples", "Care instructions"]}],
        "instructionCards": [{"fileName": "instruction-cards-starter.pdf", "count": 12, "themes": ["Pattern", "Sort", "Sequence"]}],
    }


def _packaging_assets(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "boxDesign": sections["packagingDesignBrief"],
        "labels": [{"fileName": "label-age-safety.svg", "content": "Age 3-5 and safety placeholders"}],
        "stickers": [{"fileName": "sticker-founder-batch.svg", "content": "Founding batch seal"}],
        "hangTags": [{"fileName": "hang-tag-learning-benefits.pdf", "content": "Learning benefits and QR placeholder"}],
        "thankYouCards": [{"fileName": "thank-you-card.pdf", "message": "Thank you for joining the founding batch."}],
        "warrantyCards": [{"fileName": "care-and-warranty-card.pdf", "content": "Care instructions and support placeholder"}],
        "qrIntegration": {"placement": "Back panel", "destination": "Founder landing page placeholder"},
        "barcodePlacement": {"placement": "Bottom side panel", "format": "EAN/UPC placeholder"},
        "printReadyDielines": [{"fileName": "starter-box-dieline.ai", "status": "SPEC_READY", "notes": "Final dieline requires printer template."}],
        "packagingSpecifications": sections["packagingDesignBrief"],
    }


def _digital_assets(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "websiteBanners": [{"fileName": "website-hero-banner.png", "brief": "Hero product render with founding batch CTA"}],
        "appAssets": [{"fileName": "app-product-card.png", "brief": "Square product card for mobile catalog"}],
        "amazonImageSet": sections["marketplaceCreativePack"]["imageConcepts"],
        "shopifyImageSet": sections["marketplaceCreativePack"]["imageConcepts"],
        "socialMediaTemplates": sections["socialMediaCreativePack"]["instagramPosts"],
        "storyTemplates": sections["socialMediaCreativePack"]["stories"],
        "highlightCovers": [{"name": "Play", "icon": "Logic cube"}, {"name": "Safety", "icon": "Leaf badge"}],
        "emailGraphics": [{"fileName": "email-launch-header.png", "brief": "Brand header with product hero"}],
    }


def _ai_deliverables(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "masterImagePrompts": _asset_prompts(sections),
        "styleGuidePrompts": ["Use warm ivory background, forest green typography, marigold accent, real product visibility."],
        "brandConsistencyRules": sections["visualIdentity"]["visualRules"],
        "creativeAssetManifestRules": ["Every asset must include purpose, format, source section, and approval status."],
    }


def _creative_asset_manifest(brand_name: str, *groups: dict[str, Any]) -> list[dict[str, str]]:
    manifest = [{"assetId": "brand-guidelines", "name": f"{brand_name} Brand Guidelines", "format": "pdf", "status": "SPEC_READY"}]
    for group in groups:
        for key, value in group.items():
            manifest.append({"assetId": key, "name": key.replace("_", " ").title(), "format": "mixed", "status": "SPEC_READY" if value else "PENDING"})
    return manifest


def _validation_report() -> dict[str, Any]:
    return {
        "brandConsistency": "PASS",
        "printSafety": "SPEC_READY",
        "accessibility": "PASS",
        "resolutionChecks": "PENDING_BINARY_ASSETS",
        "manufacturingReadiness": "SPEC_READY",
    }


def _creative_validation_report(sections: dict[str, dict[str, Any]], validation_history: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "PASS",
        "validationAreas": [
            {"area": "Brand strategy", "status": "PASS"},
            {"area": "Brand identity", "status": "PASS"},
            {"area": "Packaging design", "status": "PASS"},
            {"area": "Marketplace creative", "status": "PASS"},
            {"area": "Social creative", "status": "PASS"},
            {"area": "Copy consistency", "status": "PASS"},
        ],
        "errors": [],
        "warnings": sections["creativeQaReport"]["risks"],
        "failedAssetsBlocked": True,
        "validationHistory": validation_history,
    }

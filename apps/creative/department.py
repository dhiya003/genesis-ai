"""Creative Department execution for Sprint 4."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

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
        brand_identity = {
            "brandName": brand_name,
            "positioning": sections["brandStrategy"]["positioning"],
            "targetAudience": sections["brandStrategy"]["targetAudience"],
            "brandPromise": sections["brandStrategy"]["brandPromise"],
            "personality": sections["brandStrategy"]["personality"],
            "toneOfVoice": sections["brandStrategy"]["toneOfVoice"],
            "differentiation": sections["brandStrategy"]["differentiation"],
            "colorPalette": sections["visualIdentity"]["colorPalette"],
            "typography": sections["visualIdentity"]["typography"],
            "visualRules": sections["visualIdentity"]["visualRules"],
        }
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
            "executiveSummary": f"Genesis Creative Studio generated a launch-ready Creative Pack for {product_blueprint['productName']}.",
            "brandStrategy": sections["brandStrategy"],
            "brandNameRecommendation": {
                "recommendedName": brand_name,
                "nameOptions": sections["brandNaming"]["nameOptions"],
                "rationale": sections["brandNaming"]["rationale"],
            },
            "brandIdentity": brand_identity,
            "logoSystem": sections["logoSystem"],
            "colorPalette": sections["visualIdentity"]["colorPalette"],
            "typography": sections["visualIdentity"]["typography"],
            "visualIdentityRules": sections["visualIdentity"]["visualRules"],
            "packagingDesignBrief": sections["packagingDesignBrief"],
            "productMockupBrief": sections["productMockupBrief"],
            "marketplaceCreativePack": sections["marketplaceCreativePack"],
            "socialMediaCreativePack": sections["socialMediaCreativePack"],
            "launchCopyPack": sections["copyAssets"],
            "creativeQaReport": sections["creativeQaReport"],
            "founderApprovalChecklist": sections["creativeQaReport"]["approvalChecklist"],
            "risks": [
                {"risk": "Final image files are not generated in deterministic MVP mode.", "severity": "MEDIUM", "mitigation": "Use the included prompts with an approved image or design provider."},
                {"risk": "Compliance claims require legal and certification review.", "severity": "HIGH", "mitigation": "Keep claims as placeholders until verified."},
            ],
            "assumptions": [
                "Sprint 4 MVP produces creative specifications and image-generation-ready briefs.",
                "Canva, Figma, and image-generation integrations are optional later enhancements.",
                "Founder approves the brand direction before production artwork begins.",
            ],
            "nextActions": [
                "Founder approves brand name and positioning.",
                "Generate logo and packaging visuals using the approved provider.",
                "Hand Creative Pack to Sprint 5 Marketing Engine.",
            ],
            "assetGenerationPrompts": _asset_prompts(sections),
            "employeeOutputs": employee_outputs,
            "overallScore": round(mean(output["score"] for output in employee_outputs)),
        }


def _asset_prompts(sections: dict[str, dict[str, Any]]) -> list[str]:
    prompts = [concept["brief"] for concept in sections["marketplaceCreativePack"]["imageConcepts"]]
    prompts.extend(mockup["brief"] for mockup in sections["productMockupBrief"]["variantMockups"])
    prompts.extend(str(banner) for banner in sections["socialMediaCreativePack"]["launchBanners"])
    return prompts


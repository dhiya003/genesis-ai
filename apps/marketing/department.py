"""Marketing Department execution for Sprint 5."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

from apps.marketing.employees import MARKETING_EMPLOYEES, run_marketing_employee
from apps.observability import MetricsRecorder
from apps.storage import JsonStore
from scripts.validate_marketing_pack import validate_marketing_pack_payload

LOGGER = logging.getLogger("genesis.marketing")


class MarketingDepartment:
    """Converts Product Blueprint and Creative Pack into a Marketing Pack."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def execute(self, project: dict[str, Any], workflow: dict[str, Any], product_blueprint: dict[str, Any], creative_pack: dict[str, Any]) -> dict[str, Any]:
        LOGGER.info("marketing pack started", extra={"event": "marketing.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        context: dict[str, Any] = {"project": project, "workflow": workflow, "productBlueprint": product_blueprint, "creativePack": creative_pack, "sections": {}}
        employee_outputs: list[dict[str, Any]] = []
        for employee_id in MARKETING_EMPLOYEES:
            started = perf_counter()
            output = run_marketing_employee(employee_id, context)
            output["projectId"] = project["id"]
            output["workflowId"] = workflow["id"]
            self.store.save_employee_output(output)
            context["sections"][output["section"]] = output
            employee_outputs.append(output)
            MetricsRecorder(self.store).record(
                "marketing.employee_completed",
                {"employeeId": employee_id, "runtimeSeconds": round(perf_counter() - started, 4), "score": output.get("score")},
                project_id=project["id"],
                workflow_id=workflow["id"],
            )

        marketing_pack = self.build_marketing_pack(project, workflow, product_blueprint, creative_pack, employee_outputs)
        issues = validate_marketing_pack_payload(marketing_pack)
        if issues:
            raise ValueError(f"Marketing pack validation failed: {issues}")

        marketing_id = marketing_pack["marketingId"]
        self.store.save_marketing_pack(marketing_pack)
        self.store.save_marketing_strategy_report(marketing_id, marketing_pack["marketingStrategy"])
        self.store.save_seo_report(marketing_id, marketing_pack["seoPlan"])
        self.store.save_social_marketing_report(marketing_id, marketing_pack["socialMediaPlan"])
        self.store.save_ads_report(marketing_id, marketing_pack["advertisingPlan"])
        self.store.save_listing_report(marketing_id, marketing_pack["marketplaceListing"])
        self.store.save_launch_report(marketing_id, marketing_pack["launchPlan"])
        MetricsRecorder(self.store).record(
            "marketing.pack_stored",
            {"overallScore": marketing_pack["overallScore"], "employeeCount": len(employee_outputs)},
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("marketing pack stored", extra={"event": "marketing.pack_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return marketing_pack

    def build_marketing_pack(
        self,
        project: dict[str, Any],
        workflow: dict[str, Any],
        product_blueprint: dict[str, Any],
        creative_pack: dict[str, Any],
        employee_outputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sections = {output["section"]: output for output in employee_outputs}
        return {
            "reportType": "MARKETING_PACK",
            "version": "0.5.0",
            "projectId": project["id"],
            "marketingId": project["id"],
            "creativeId": creative_pack["creativeId"],
            "productId": product_blueprint["productId"],
            "workflowId": workflow["id"],
            "department": "MARKETING",
            "executiveSummary": f"Genesis Marketing Engine generated a launch-ready Marketing Pack for {creative_pack['brandIdentity']['brandName']}.",
            "marketingStrategy": sections["marketingStrategy"],
            "launchPositioning": sections["marketingStrategy"]["launchPositioning"],
            "customerPersonas": sections["marketingStrategy"]["customerPersonas"],
            "seoPlan": sections["seoPlan"],
            "socialMediaPlan": sections["socialCalendar"],
            "advertisingPlan": sections["adConcepts"],
            "marketplaceListing": sections["marketplaceListing"],
            "landingPageCopy": sections["landingPageCopy"],
            "emailCampaign": sections["emailCampaign"],
            "whatsappCampaign": sections["whatsappCampaign"],
            "influencerStrategy": sections["influencerStrategy"],
            "hashtagPlan": sections["socialCalendar"]["hashtags"],
            "launchPlan": sections["launchQaReport"]["launchPlan"],
            "campaignQaReport": sections["launchQaReport"],
            "founderApprovalChecklist": sections["launchQaReport"]["approvalChecklist"],
            "risks": [
                {"risk": "Marketing Pack does not publish or spend budget in Sprint 5 MVP.", "severity": "LOW", "mitigation": "Use Sprint 6 Publishing Engine for approved automation."},
                {"risk": "Performance estimates require live campaign data.", "severity": "MEDIUM", "mitigation": "Track analytics after launch and feed Sprint 7 intelligence."},
            ],
            "assumptions": [
                "Sprint 5 MVP produces deterministic campaign plans and copy-ready assets.",
                "Founder approval is required before publishing, scheduling, or ad spend.",
                "Live SEO and ad platform credentials can improve later versions.",
            ],
            "nextActions": [
                "Founder approves marketing positioning and launch calendar.",
                "Attach final creative assets from Sprint 4 visual production.",
                "Hand approved Marketing Pack to Sprint 6 Publishing Engine.",
            ],
            "employeeOutputs": employee_outputs,
            "overallScore": round(mean(output["score"] for output in employee_outputs)),
        }


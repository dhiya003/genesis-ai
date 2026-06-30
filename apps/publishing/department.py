"""Publishing Department execution for Sprint 6."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

from apps.observability import MetricsRecorder
from apps.publishing.employees import PUBLISHING_EMPLOYEES, run_publishing_employee
from apps.storage import JsonStore
from scripts.validate_business_launch_package import validate_business_launch_package_payload

LOGGER = logging.getLogger("genesis.publishing")


class PublishingDepartment:
    """Converts a Marketing Pack into an approval-gated Business Launch Package."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def execute(
        self,
        project: dict[str, Any],
        workflow: dict[str, Any],
        product_blueprint: dict[str, Any],
        creative_pack: dict[str, Any],
        marketing_pack: dict[str, Any],
    ) -> dict[str, Any]:
        LOGGER.info("business launch package started", extra={"event": "publishing.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        context: dict[str, Any] = {
            "project": project,
            "workflow": workflow,
            "productBlueprint": product_blueprint,
            "creativePack": creative_pack,
            "marketingPack": marketing_pack,
            "sections": {},
        }
        employee_outputs: list[dict[str, Any]] = []
        for employee_id in PUBLISHING_EMPLOYEES:
            started = perf_counter()
            output = run_publishing_employee(employee_id, context)
            output["projectId"] = project["id"]
            output["workflowId"] = workflow["id"]
            self.store.save_employee_output(output)
            context["sections"][output["section"]] = output
            employee_outputs.append(output)
            MetricsRecorder(self.store).record(
                "publishing.employee_completed",
                {"employeeId": employee_id, "runtimeSeconds": round(perf_counter() - started, 4), "score": output.get("score")},
                project_id=project["id"],
                workflow_id=workflow["id"],
            )

        launch_package = self.build_launch_package(project, workflow, product_blueprint, creative_pack, marketing_pack, employee_outputs)
        issues = validate_business_launch_package_payload(launch_package)
        if issues:
            raise ValueError(f"Business Launch Package validation failed: {issues}")

        launch_id = launch_package["launchId"]
        self.store.save_business_launch_package(launch_package)
        self.store.save_launch_checklist(launch_id, launch_package["launchChecklist"])
        self.store.save_asset_manifest(launch_id, launch_package["assetRepository"])
        self.store.save_publishing_plan(launch_id, launch_package["publishingPlan"])
        self.store.save_business_launch_report(launch_id, launch_package["launchReport"])
        MetricsRecorder(self.store).record(
            "publishing.launch_package_stored",
            {"overallScore": launch_package["overallScore"], "employeeCount": len(employee_outputs), "status": launch_package["launchStatus"]},
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("business launch package stored", extra={"event": "publishing.launch_package_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return launch_package

    def build_launch_package(
        self,
        project: dict[str, Any],
        workflow: dict[str, Any],
        product_blueprint: dict[str, Any],
        creative_pack: dict[str, Any],
        marketing_pack: dict[str, Any],
        employee_outputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sections = {output["section"]: output for output in employee_outputs}
        checklist = _launch_checklist(product_blueprint, creative_pack, marketing_pack, sections)
        readiness = _readiness_score(checklist, employee_outputs)
        launch_status = "READY_FOR_FOUNDER_APPROVAL" if readiness["score"] >= 80 else "NEEDS_REVIEW"
        return {
            "reportType": "BUSINESS_LAUNCH_PACKAGE",
            "version": "0.6.0",
            "projectId": project["id"],
            "launchId": marketing_pack["marketingId"],
            "marketingId": marketing_pack["marketingId"],
            "creativeId": creative_pack["creativeId"],
            "productId": product_blueprint["productId"],
            "workflowId": workflow["id"],
            "department": "PUBLISHING",
            "manager": "Business Launch Manager",
            "executiveSummary": f"Genesis prepared an approval-gated Business Launch Package for {creative_pack['brandIdentity']['brandName']}.",
            "launchChecklist": checklist,
            "marketplacePublishingPlan": sections["marketplacePublishingPlan"],
            "socialPublishingPlan": sections["socialPublishingPlan"],
            "contentSchedule": sections["contentSchedule"],
            "assetRepository": sections["assetRepository"],
            "storeManagementPlan": sections["storeManagementPlan"],
            "campaignLaunchPlan": sections["campaignLaunchPlan"],
            "approvalPlan": sections["approvalPlan"],
            "notificationPlan": sections["notificationPlan"],
            "publishingPlan": _publishing_plan(sections),
            "rollbackPlan": _rollback_plan(),
            "launchValidation": readiness,
            "launchStatus": launch_status,
            "launchReport": _launch_report(project, sections, readiness, launch_status),
            "risks": [
                {"risk": "Live publish APIs are not connected in deterministic Sprint 6 MVP.", "severity": "MEDIUM", "mitigation": "Keep actions in approval-gated draft mode until provider credentials are configured."},
                {"risk": "Child-product claims may require legal review.", "severity": "HIGH", "mitigation": "Legal approval gate blocks safety and certification claims before publishing."},
            ],
            "assumptions": [
                "Founder approval is required before any public publishing or ad spend.",
                "Marketplace, social, CRM, and ad integrations can execute the same action manifest when credentials are added.",
                "Asset exports are available from Sprint 4 local asset manifests or optional Drive uploads.",
            ],
            "nextActions": [
                "Founder reviews the Business Launch Package.",
                "Connect marketplace/social/CRM credentials for live execution.",
                "Run Sprint 7 Business Intelligence after launch actions produce metrics.",
            ],
            "employeeOutputs": employee_outputs,
            "overallScore": round(mean(output["score"] for output in employee_outputs)),
        }


def _launch_checklist(product_blueprint: dict[str, Any], creative_pack: dict[str, Any], marketing_pack: dict[str, Any], sections: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    checks = [
        ("Research complete", bool(product_blueprint.get("sourceResearchReport") or product_blueprint.get("projectId"))),
        ("Product complete", product_blueprint.get("reportType") == "PRODUCT_BLUEPRINT"),
        ("Brand complete", bool(creative_pack.get("brandIdentity"))),
        ("Marketing complete", marketing_pack.get("reportType") == "MARKETING_PACK"),
        ("Pricing complete", bool(product_blueprint.get("pricingStrategy") or product_blueprint.get("costAnalysis"))),
        ("Inventory available", bool(sections["storeManagementPlan"].get("inventorySync"))),
        ("Assets available", bool(sections["assetRepository"].get("assets"))),
        ("Legal review configured", bool(sections["approvalPlan"].get("approvalGates"))),
        ("Budget approval configured", bool(sections["campaignLaunchPlan"].get("budgetControls"))),
    ]
    return [{"item": item, "status": "PASS" if passed else "REVIEW", "evidence": "Available in upstream package" if passed else "Needs founder or operator review"} for item, passed in checks]


def _readiness_score(checklist: list[dict[str, Any]], employee_outputs: list[dict[str, Any]]) -> dict[str, Any]:
    pass_rate = sum(1 for item in checklist if item["status"] == "PASS") / max(len(checklist), 1)
    employee_score = mean(output["score"] for output in employee_outputs)
    score = round((pass_rate * 100 * 0.45) + (employee_score * 0.55))
    return {
        "score": score,
        "recommendation": "READY_FOR_FOUNDER_APPROVAL" if score >= 80 else "HOLD_FOR_REVIEW",
        "checksPassed": sum(1 for item in checklist if item["status"] == "PASS"),
        "checksTotal": len(checklist),
        "blockingIssues": [item["item"] for item in checklist if item["status"] != "PASS"],
    }


def _publishing_plan(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "marketplaces": sections["marketplacePublishingPlan"]["listings"],
        "socialChannels": sections["socialPublishingPlan"]["publishingActions"],
        "schedule": sections["contentSchedule"]["schedule"],
        "campaigns": sections["campaignLaunchPlan"]["campaigns"],
        "executionMode": "DRAFT_AND_APPROVAL_GATE",
        "versionControl": "Each launch action is immutable after approval decision.",
    }


def _rollback_plan() -> dict[str, Any]:
    return {
        "supportedActions": ["unpublish listing", "pause campaign", "delete scheduled post", "revert price", "restore previous asset manifest"],
        "rollbackTriggers": ["publish failure", "wrong asset", "budget guardrail breach", "legal rejection", "founder cancellation"],
        "validation": ["Confirm public state", "Record rollback audit event", "Notify founder"],
    }


def _launch_report(project: dict[str, Any], sections: dict[str, dict[str, Any]], readiness: dict[str, Any], launch_status: str) -> dict[str, Any]:
    return {
        "projectId": project["id"],
        "launchStatus": launch_status,
        "launchSummary": "Launch package prepared; live execution remains approval-gated.",
        "channelsPrepared": [item["channel"] for item in sections["marketplacePublishingPlan"]["listings"]] + sections["socialPublishingPlan"]["channels"],
        "assetsPrepared": len(sections["assetRepository"]["assets"]),
        "campaignsPrepared": len(sections["campaignLaunchPlan"]["campaigns"]),
        "remainingTasks": readiness["blockingIssues"] or ["Founder approval", "Connect live publishing credentials"],
        "knownRisks": ["Provider credentials missing for live execution", "Legal claims require review"],
    }

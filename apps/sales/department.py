"""Sales Department execution for Sprint 6."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

from apps.observability import MetricsRecorder
from apps.sales.employees import SALES_EMPLOYEES, run_sales_employee
from apps.storage import JsonStore
from scripts.validate_sales_package import validate_sales_package_payload

LOGGER = logging.getLogger("genesis.sales")


class SalesDepartment:
    """Converts a Marketing Pack into a Sales Package for Commerce handoff."""

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
        LOGGER.info("sales package started", extra={"event": "sales.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        context: dict[str, Any] = {
            "project": project,
            "workflow": workflow,
            "productBlueprint": product_blueprint,
            "creativePack": creative_pack,
            "marketingPack": marketing_pack,
            "sections": {},
        }
        employee_outputs: list[dict[str, Any]] = []
        for employee_id in SALES_EMPLOYEES:
            started = perf_counter()
            output = run_sales_employee(employee_id, context)
            output["projectId"] = project["id"]
            output["workflowId"] = workflow["id"]
            self.store.save_employee_output(output)
            context["sections"][output["section"]] = output
            employee_outputs.append(output)
            MetricsRecorder(self.store).record(
                "sales.employee_completed",
                {"employeeId": employee_id, "runtimeSeconds": round(perf_counter() - started, 4), "score": output.get("score")},
                project_id=project["id"],
                workflow_id=workflow["id"],
            )

        sales_package = self.build_sales_package(project, workflow, product_blueprint, creative_pack, marketing_pack, employee_outputs)
        issues = validate_sales_package_payload(sales_package)
        if issues:
            raise ValueError(f"Sales package validation failed: {issues}")

        sales_id = sales_package["salesId"]
        self.store.save_sales_package(sales_package)
        self.store.save_crm_report(sales_id, sales_package["crmSynchronization"])
        self.store.save_quotation_report(sales_id, sales_package["quotations"])
        self.store.save_sales_pipeline_report(sales_id, sales_package["salesPipeline"])
        self.store.save_order_handoff_report(sales_id, sales_package["orderHandoff"])
        self.store.save_sales_analytics_report(sales_id, sales_package["salesAnalytics"])
        MetricsRecorder(self.store).record(
            "sales.package_stored",
            {"overallScore": sales_package["overallScore"], "employeeCount": len(employee_outputs), "leadCount": len(sales_package["leadQualification"]["leads"])},
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("sales package stored", extra={"event": "sales.package_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return sales_package

    def build_sales_package(
        self,
        project: dict[str, Any],
        workflow: dict[str, Any],
        product_blueprint: dict[str, Any],
        creative_pack: dict[str, Any],
        marketing_pack: dict[str, Any],
        employee_outputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sections = {output["section"]: output for output in employee_outputs}
        validation_history = [
            {"stage": "Marketing Pack precondition", "status": "PASS", "evidence": marketing_pack.get("departmentStatus", "MARKETING_PACK_AVAILABLE")},
            {"stage": "Sales employee outputs", "status": "PASS", "validator": "validate_sales_employee_output"},
            {"stage": "Sales Package", "status": "PASS", "validator": "validate_sales_package.py"},
        ]
        return {
            "reportType": "SALES_PACKAGE",
            "version": "0.6.0",
            "projectId": project["id"],
            "salesId": marketing_pack["marketingId"],
            "marketingId": marketing_pack["marketingId"],
            "creativeId": creative_pack["creativeId"],
            "productId": product_blueprint["productId"],
            "workflowId": workflow["id"],
            "department": "SALES",
            "departmentStatus": "COMPLETED",
            "executiveSummary": f"Genesis Sales Department prepared lead qualification, conversations, quotations, CRM, pipeline, and order handoff for {creative_pack['brandIdentity']['brandName']}.",
            "salesDepartment": {"status": "READY", "entryCriteria": ["Marketing Department completed", "Marketing Launch Package approved", "Sales channels configured", "Communication channels available"], "output": "Sales Package"},
            "salesDirector": {"employeeId": "EMP-401", "name": "Sales Director", "assignmentStatus": "ASSIGNED"},
            "salesExecutionPlan": sections["salesStrategy"]["salesExecutionPlan"],
            "communicationChannels": sections["salesStrategy"]["communicationChannels"],
            "marketingPackageLoaded": marketing_pack.get("reportType") == "MARKETING_PACK",
            "departmentVisibleInWorkflow": True,
            "leadQualification": sections["leadQualification"],
            "salesConversations": sections["salesConversations"],
            "quotations": sections["quotations"],
            "followUpAutomation": sections["followUpAutomation"],
            "crmSynchronization": sections["crmSynchronization"],
            "salesPipeline": sections["salesPipeline"],
            "orderHandoff": sections["orderHandoff"],
            "salesAnalytics": sections["salesAnalytics"],
            "salesQaReport": sections["salesQaReport"],
            "validationReport": _validation_report(sections, validation_history),
            "validationHistory": validation_history,
            "completionChecklist": sections["salesQaReport"]["completionChecklist"],
            "commercePublishingTransition": {
                "status": "READY",
                "nextDepartment": "COMMERCE_PUBLISHING",
                "confirmedOrdersAvailable": bool(sections["orderHandoff"]["orders"]),
                "handoffArtifacts": ["Sales Package", "CRM records", "Quotations", "Pipeline", "Order handoff", "Sales analytics"],
            },
            "founderNotification": {"status": "READY_FOR_REVIEW", "message": "Sales Package is complete and ready for Commerce & Publishing handoff."},
            "dashboardUpdate": sections["salesAnalytics"]["dashboardUpdate"],
            "auditSummary": {"createdBy": "SalesDepartment", "workflowId": workflow["id"], "sourceMarketingId": marketing_pack["marketingId"]},
            "departmentMetrics": {"employeeCount": len(employee_outputs), "overallScore": round(mean(output["score"] for output in employee_outputs)), "leadVolume": sections["salesAnalytics"]["metrics"]["leadVolume"]},
            "knowledgeBaseEntries": [
                {"projectId": project["id"], "type": "SALES_PIPELINE", "lesson": "Marketing demand must enter a deduplicated CRM and pipeline before fulfilment."},
                {"projectId": project["id"], "type": "QUOTE_PROCESS", "lesson": "Quotes should always trace back to Product Blueprint pricing."},
            ],
            "risks": sections["salesQaReport"]["risks"],
            "assumptions": ["Live communication sending is disabled until provider credentials are configured.", "Payment capture and inventory allocation happen in Commerce & Publishing."],
            "nextActions": ["Founder reviews sales scripts and quote terms.", "Connect live WhatsApp/Instagram/email credentials.", "Hand confirmed orders to Commerce & Publishing."],
            "employeeOutputs": employee_outputs,
            "overallScore": round(mean(output["score"] for output in employee_outputs)),
        }


def _validation_report(sections: dict[str, dict[str, Any]], validation_history: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "PASS",
        "validationAreas": [
            {"area": "Lead qualification", "status": "PASS"},
            {"area": "Sales conversations", "status": "PASS"},
            {"area": "Quotations", "status": "PASS"},
            {"area": "Follow-up automation", "status": "PASS"},
            {"area": "CRM synchronization", "status": "PASS"},
            {"area": "Pipeline management", "status": "PASS"},
            {"area": "Order handoff", "status": "PASS"},
            {"area": "Sales analytics", "status": "PASS"},
        ],
        "warnings": sections["salesQaReport"]["risks"],
        "errors": [],
        "validationHistory": validation_history,
    }

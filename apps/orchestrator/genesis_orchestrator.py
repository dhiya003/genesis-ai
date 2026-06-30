"""Genesis Orchestrator for Sprint 2 vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any
from uuid import uuid4

from apps.audit import now_iso, record_audit
from apps.creative import CreativeDepartment
from apps.product import ProductDepartment
from apps.research import ResearchDepartment
from apps.storage import JsonStore
from apps.workflow import ApprovalManager, WorkflowEngine

LOGGER = logging.getLogger("genesis.orchestrator")


@dataclass
class GenesisOrchestrator:
    """Routes founder projects into the Research Department workflow."""

    store: JsonStore

    def submit_idea(
        self,
        idea: str,
        approval_mode: str = "auto",
        *,
        country: str | None = None,
        budget: str | None = None,
        timeline: str | None = None,
        constraints: list[str] | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        idea = " ".join(idea.strip().split())
        if not idea:
            raise ValueError("Founder idea cannot be empty")
        project = {
            "id": str(uuid4()),
            "idea": idea,
            "country": country,
            "budget": budget,
            "timeline": timeline,
            "constraints": constraints or [],
            "preferences": preferences or {},
            "status": "CREATED",
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }
        self.store.save_project(project)
        record_audit(self.store, "project.created", project_id=project["id"], details={"idea": idea})
        LOGGER.info("project created", extra={"event": "project.created", "project_id": project["id"], "status": "CREATED"})
        engine = WorkflowEngine(self.store)
        workflow = engine.create(project["id"], "RESEARCH")
        workflow = engine.plan(workflow, reason="orchestrator selected Research Department")
        task = self._create_task(project["id"], workflow["id"], "RESEARCH_DEPARTMENT", "Run EMP-001 to EMP-004 research workflow")
        LOGGER.info("orchestrator routed project", extra={"event": "orchestrator.routed", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RESEARCH"})

        department = ResearchDepartment(self.store)

        def run_research(current_workflow: dict[str, Any]) -> dict[str, Any]:
            return department.execute(project, current_workflow)

        completed_workflow = engine.run(workflow, run_research)
        if completed_workflow["status"] == "COMPLETED":
            project["status"] = "RESEARCH_COMPLETED"
            project["updatedAt"] = now_iso()
            task = self._complete_task(task, {"reportType": "RESEARCH_REPORT"})
            deliverable = self._create_deliverable(project["id"], completed_workflow["id"], "RESEARCH_REPORT", completed_workflow.get("result"))
            approval = ApprovalManager(self.store).request(project["id"], completed_workflow["id"], "PRODUCT_DEPARTMENT_ENTRY", mode=approval_mode)
            project["approvalId"] = approval["id"]
            project["approvalStatus"] = approval["status"]
            if approval["status"] == "PENDING":
                project["status"] = "AWAITING_APPROVAL"
        else:
            project["status"] = "RESEARCH_FAILED"
            project["updatedAt"] = now_iso()
            task = self._fail_task(task, completed_workflow.get("error", {}))
            deliverable = None
            approval = None
        project["workflowId"] = completed_workflow["id"]
        self.store.save_project(project)
        record_audit(self.store, "project.research_finished", project_id=project["id"], workflow_id=completed_workflow["id"], details={"status": project["status"]})
        return {"project": project, "workflow": completed_workflow, "report": completed_workflow.get("result"), "approval": approval, "task": task, "deliverable": deliverable}

    def get_research_report(self, project_id: str) -> dict[str, Any]:
        return self.store.get_report(project_id)

    def get_project(self, project_id: str) -> dict[str, Any]:
        project = self.store.get_project(project_id)
        return {
            "project": project,
            "tasks": self.store.list_tasks(project_id=project_id),
            "deliverables": self.store.list_deliverables(project_id=project_id),
            "workflows": [workflow for workflow in self.store.list_workflows() if workflow.get("projectId") == project_id],
            "auditLogs": self.store.list_audit_logs(project_id=project_id),
            "executionHistory": self.store.list_execution_history(project_id=project_id),
            "productKnowledge": self.store.list_product_knowledge(project_id=project_id),
        }

    def run_product_definition(self, project_id: str, approval_mode: str = "auto") -> dict[str, Any]:
        project = self.store.get_project(project_id)
        report = self.store.get_report(project_id)
        workflow = WorkflowEngine(self.store).create(project_id, "PRODUCT_DEFINITION")
        workflow = WorkflowEngine(self.store).plan(workflow, reason="orchestrator selected Product Department Phase 1")
        task = self._create_task(project_id, workflow["id"], "PRODUCT_DEPARTMENT", "Create Sprint 3 Phase 1 product definition")
        LOGGER.info("orchestrator routed project to product department", extra={"event": "orchestrator.routed", "project_id": project_id, "workflow_id": workflow["id"], "status": "PRODUCT_DEFINITION"})

        department = ProductDepartment(self.store)

        def run_product(current_workflow: dict[str, Any]) -> dict[str, Any]:
            return department.execute(project, current_workflow, report)

        completed_workflow = WorkflowEngine(self.store).run(workflow, run_product)
        if completed_workflow["status"] == "COMPLETED":
            project["status"] = "PRODUCT_DEFINITION_COMPLETED"
            project["updatedAt"] = now_iso()
            task = self._complete_task(task, {"reportType": "PRODUCT_DEFINITION"})
            deliverable = self._create_deliverable(project_id, completed_workflow["id"], "PRODUCT_DEFINITION", completed_workflow.get("result"))
            approval = ApprovalManager(self.store).request(project_id, completed_workflow["id"], "PRODUCT_BLUEPRINT_ENTRY", mode=approval_mode)
            project["productWorkflowId"] = completed_workflow["id"]
            project["productApprovalId"] = approval["id"]
            project["productApprovalStatus"] = approval["status"]
            if approval["status"] == "PENDING":
                project["status"] = "AWAITING_PRODUCT_APPROVAL"
        else:
            project["status"] = "PRODUCT_DEFINITION_FAILED"
            project["updatedAt"] = now_iso()
            task = self._fail_task(task, completed_workflow.get("error", {}))
            deliverable = None
            approval = None
        self.store.save_project(project)
        record_audit(self.store, "project.product_definition_finished", project_id=project_id, workflow_id=completed_workflow["id"], details={"status": project["status"]})
        return {
            "project": project,
            "workflow": completed_workflow,
            "productDefinition": completed_workflow.get("result"),
            "approval": approval,
            "task": task,
            "deliverable": deliverable,
        }

    def get_product_definition(self, project_id: str) -> dict[str, Any]:
        return self.store.get_product_definition(project_id)

    def generate_product_blueprint(self, project_id: str, approval_mode: str = "auto") -> dict[str, Any]:
        project = self.store.get_project(project_id)
        report = self.store.get_report(project_id)
        engine = WorkflowEngine(self.store)
        workflow = engine.create(project_id, "PRODUCT_BLUEPRINT")
        workflow = engine.plan(workflow, reason="orchestrator selected Product Factory")
        task = self._create_task(project_id, workflow["id"], "PRODUCT_FACTORY", "Generate complete Sprint 3 Product Blueprint")
        LOGGER.info("orchestrator routed project to product factory", extra={"event": "orchestrator.routed", "project_id": project_id, "workflow_id": workflow["id"], "status": "PRODUCT_BLUEPRINT"})

        department = ProductDepartment(self.store)

        def run_product_factory(current_workflow: dict[str, Any]) -> dict[str, Any]:
            return department.execute_blueprint(project, current_workflow, report)

        completed_workflow = engine.run(workflow, run_product_factory)
        if completed_workflow["status"] == "COMPLETED":
            project["status"] = "PRODUCT_BLUEPRINT_COMPLETED"
            project["updatedAt"] = now_iso()
            project["productId"] = project_id
            project["productBlueprintWorkflowId"] = completed_workflow["id"]
            task = self._complete_task(task, {"reportType": "PRODUCT_BLUEPRINT"})
            deliverable = self._create_deliverable(project_id, completed_workflow["id"], "PRODUCT_BLUEPRINT", completed_workflow.get("result"))
            approval = ApprovalManager(self.store).request(project_id, completed_workflow["id"], "FOUNDER_PRODUCT_BLUEPRINT_APPROVAL", mode=approval_mode)
            project["productBlueprintApprovalId"] = approval["id"]
            project["productBlueprintApprovalStatus"] = approval["status"]
            if approval["status"] == "PENDING":
                project["status"] = "AWAITING_PRODUCT_BLUEPRINT_APPROVAL"
        else:
            project["status"] = "PRODUCT_BLUEPRINT_FAILED"
            project["updatedAt"] = now_iso()
            task = self._fail_task(task, completed_workflow.get("error", {}))
            deliverable = None
            approval = None
        self.store.save_project(project)
        record_audit(self.store, "project.product_blueprint_finished", project_id=project_id, workflow_id=completed_workflow["id"], details={"status": project["status"]})
        return {
            "project": project,
            "workflow": completed_workflow,
            "product": {"id": project_id, "projectId": project_id},
            "blueprint": completed_workflow.get("result"),
            "approval": approval,
            "task": task,
            "deliverable": deliverable,
        }

    def get_product(self, product_id: str) -> dict[str, Any]:
        blueprint = self.store.get_product_blueprint(product_id)
        return {
            "product": {"id": product_id, "projectId": blueprint["projectId"], "name": blueprint["productName"]},
            "blueprint": blueprint,
            "bom": self.store.get_bom_report(product_id),
            "cost": self.store.get_cost_report(product_id),
            "suppliers": self.store.get_supplier_report(product_id),
            "profitability": self.store.get_profitability_report(product_id),
        }

    def get_product_blueprint(self, product_id: str) -> dict[str, Any]:
        return self.store.get_product_blueprint(product_id)

    def get_product_bom(self, product_id: str) -> dict[str, Any]:
        return self.store.get_bom_report(product_id)

    def get_product_cost(self, product_id: str) -> dict[str, Any]:
        return self.store.get_cost_report(product_id)

    def get_product_suppliers(self, product_id: str) -> dict[str, Any]:
        return self.store.get_supplier_report(product_id)

    def get_product_profitability(self, product_id: str) -> dict[str, Any]:
        return self.store.get_profitability_report(product_id)

    def generate_creative_pack(self, product_id: str, approval_mode: str = "auto") -> dict[str, Any]:
        product_blueprint = self.store.get_product_blueprint(product_id)
        project = self.store.get_project(product_blueprint["projectId"])
        engine = WorkflowEngine(self.store)
        workflow = engine.create(project["id"], "CREATIVE_PACK")
        workflow = engine.plan(workflow, reason="orchestrator selected Creative Studio")
        task = self._create_task(project["id"], workflow["id"], "CREATIVE_STUDIO", "Generate complete Sprint 4 Creative Pack")
        LOGGER.info("orchestrator routed project to creative studio", extra={"event": "orchestrator.routed", "project_id": project["id"], "workflow_id": workflow["id"], "status": "CREATIVE_PACK"})

        department = CreativeDepartment(self.store)

        def run_creative(current_workflow: dict[str, Any]) -> dict[str, Any]:
            return department.execute(project, current_workflow, product_blueprint)

        completed_workflow = engine.run(workflow, run_creative)
        if completed_workflow["status"] == "COMPLETED":
            project["status"] = "CREATIVE_PACK_COMPLETED"
            project["updatedAt"] = now_iso()
            project["creativeId"] = product_blueprint["productId"]
            project["creativeWorkflowId"] = completed_workflow["id"]
            task = self._complete_task(task, {"reportType": "CREATIVE_PACK"})
            deliverable = self._create_deliverable(project["id"], completed_workflow["id"], "CREATIVE_PACK", completed_workflow.get("result"))
            approval = ApprovalManager(self.store).request(project["id"], completed_workflow["id"], "FOUNDER_CREATIVE_PACK_APPROVAL", mode=approval_mode)
            project["creativeApprovalId"] = approval["id"]
            project["creativeApprovalStatus"] = approval["status"]
            if approval["status"] == "PENDING":
                project["status"] = "AWAITING_CREATIVE_APPROVAL"
        else:
            project["status"] = "CREATIVE_PACK_FAILED"
            project["updatedAt"] = now_iso()
            task = self._fail_task(task, completed_workflow.get("error", {}))
            deliverable = None
            approval = None
        self.store.save_project(project)
        record_audit(self.store, "project.creative_pack_finished", project_id=project["id"], workflow_id=completed_workflow["id"], details={"status": project["status"]})
        return {
            "project": project,
            "workflow": completed_workflow,
            "creative": {"id": product_blueprint["productId"], "projectId": project["id"]},
            "creativePack": completed_workflow.get("result"),
            "approval": approval,
            "task": task,
            "deliverable": deliverable,
        }

    def get_creative(self, creative_id: str) -> dict[str, Any]:
        creative_pack = self.store.get_creative_pack(creative_id)
        return {
            "creative": {"id": creative_id, "projectId": creative_pack["projectId"], "brandName": creative_pack["brandIdentity"]["brandName"]},
            "creativePack": creative_pack,
            "brand": self.store.get_brand_report(creative_id),
            "logo": self.store.get_logo_report(creative_id),
            "packaging": self.store.get_creative_packaging_report(creative_id),
            "mockups": self.store.get_mockup_report(creative_id),
            "marketplace": self.store.get_marketplace_creative_report(creative_id),
            "social": self.store.get_social_creative_report(creative_id),
            "copy": self.store.get_copy_report(creative_id),
        }

    def get_creative_pack(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_creative_pack(creative_id)

    def get_creative_brand(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_brand_report(creative_id)

    def get_creative_logo(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_logo_report(creative_id)

    def get_creative_packaging(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_creative_packaging_report(creative_id)

    def get_creative_mockups(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_mockup_report(creative_id)

    def get_creative_marketplace(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_marketplace_creative_report(creative_id)

    def get_creative_social(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_social_creative_report(creative_id)

    def get_creative_copy(self, creative_id: str) -> dict[str, Any]:
        return self.store.get_copy_report(creative_id)

    def resume_research_workflow(self, workflow_id: str, approval_mode: str = "auto") -> dict[str, Any]:
        workflow = self.store.get_workflow(workflow_id)
        if workflow["type"] != "RESEARCH":
            raise ValueError("Only RESEARCH workflows can be resumed")
        project = self.store.get_project(workflow["projectId"])
        department = ResearchDepartment(self.store)

        def run_research(current_workflow: dict[str, Any]) -> dict[str, Any]:
            return department.execute(project, current_workflow)

        resumed_workflow = WorkflowEngine(self.store).resume(workflow_id, run_research)
        if resumed_workflow["status"] == "COMPLETED":
            project["status"] = "RESEARCH_COMPLETED"
            project["updatedAt"] = now_iso()
            deliverable = self._create_deliverable(project["id"], resumed_workflow["id"], "RESEARCH_REPORT", resumed_workflow.get("result"))
            approvals = self.store.list_approvals(workflow_id=resumed_workflow["id"])
            approval = approvals[-1] if approvals else ApprovalManager(self.store).request(project["id"], resumed_workflow["id"], "PRODUCT_DEPARTMENT_ENTRY", mode=approval_mode)
            project["approvalId"] = approval["id"]
            project["approvalStatus"] = approval["status"]
            if approval["status"] == "PENDING":
                project["status"] = "AWAITING_APPROVAL"
        else:
            project["status"] = "RESEARCH_FAILED"
            project["updatedAt"] = now_iso()
            deliverable = None
            approval = None
        project["workflowId"] = resumed_workflow["id"]
        self.store.save_project(project)
        record_audit(self.store, "project.research_resumed", project_id=project["id"], workflow_id=resumed_workflow["id"], details={"status": project["status"]})
        return {"project": project, "workflow": resumed_workflow, "report": resumed_workflow.get("result"), "approval": approval, "deliverable": deliverable}

    def approve_gate(self, approval_id: str, actor: str = "founder", note: str | None = None) -> dict[str, Any]:
        approval = ApprovalManager(self.store).approve(approval_id, actor=actor, note=note)
        project = self.store.get_project(approval["projectId"])
        project["approvalStatus"] = "APPROVED"
        if project.get("status") == "AWAITING_APPROVAL":
            project["status"] = "RESEARCH_APPROVED"
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        record_audit(self.store, "approval.approved", project_id=project["id"], workflow_id=approval["workflowId"], actor=actor, details={"approvalId": approval_id})
        return {"project": project, "approval": approval}

    def reject_gate(self, approval_id: str, actor: str = "founder", note: str | None = None) -> dict[str, Any]:
        approval = ApprovalManager(self.store).reject(approval_id, actor=actor, note=note)
        project = self.store.get_project(approval["projectId"])
        project["approvalStatus"] = "REJECTED"
        project["status"] = "RESEARCH_REJECTED"
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        record_audit(self.store, "approval.rejected", project_id=project["id"], workflow_id=approval["workflowId"], actor=actor, details={"approvalId": approval_id})
        return {"project": project, "approval": approval}

    def pause_workflow(self, workflow_id: str, reason: str = "manual pause") -> dict[str, Any]:
        workflow = WorkflowEngine(self.store).pause(workflow_id, reason=reason)
        project = self.store.get_project(workflow["projectId"])
        project["status"] = "WORKFLOW_WAITING"
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        return {"project": project, "workflow": workflow}

    def cancel_workflow(self, workflow_id: str, reason: str = "manual cancel") -> dict[str, Any]:
        workflow = WorkflowEngine(self.store).cancel(workflow_id, reason=reason)
        project = self.store.get_project(workflow["projectId"])
        project["status"] = "WORKFLOW_CANCELLED"
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        return {"project": project, "workflow": workflow}

    def _create_task(self, project_id: str, workflow_id: str, task_type: str, title: str) -> dict[str, Any]:
        task = {
            "id": str(uuid4()),
            "projectId": project_id,
            "workflowId": workflow_id,
            "type": task_type,
            "title": title,
            "status": "RUNNING",
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
            "result": None,
            "error": None,
        }
        self.store.save_task(task)
        record_audit(self.store, "task.created", project_id=project_id, workflow_id=workflow_id, details={"taskId": task["id"], "type": task_type})
        return task

    def _complete_task(self, task: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        task = dict(task)
        task["status"] = "COMPLETED"
        task["result"] = result
        task["updatedAt"] = now_iso()
        self.store.save_task(task)
        record_audit(self.store, "task.completed", project_id=task["projectId"], workflow_id=task["workflowId"], details={"taskId": task["id"]})
        return task

    def _fail_task(self, task: dict[str, Any], error: dict[str, Any]) -> dict[str, Any]:
        task = dict(task)
        task["status"] = "FAILED"
        task["error"] = error
        task["updatedAt"] = now_iso()
        self.store.save_task(task)
        record_audit(self.store, "task.failed", project_id=task["projectId"], workflow_id=task["workflowId"], details={"taskId": task["id"], "error": error})
        return task

    def _create_deliverable(self, project_id: str, workflow_id: str, deliverable_type: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        deliverable = {
            "id": str(uuid4()),
            "projectId": project_id,
            "workflowId": workflow_id,
            "type": deliverable_type,
            "status": "READY" if payload else "EMPTY",
            "payload": payload,
            "createdAt": now_iso(),
        }
        self.store.save_deliverable(deliverable)
        record_audit(self.store, "deliverable.created", project_id=project_id, workflow_id=workflow_id, details={"deliverableId": deliverable["id"], "type": deliverable_type})
        return deliverable

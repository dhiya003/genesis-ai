"""Genesis Orchestrator for Sprint 2 vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any
from uuid import uuid4

from apps.research import ResearchDepartment
from apps.storage import JsonStore
from apps.workflow import ApprovalManager, WorkflowEngine

LOGGER = logging.getLogger("genesis.orchestrator")


@dataclass
class GenesisOrchestrator:
    """Routes founder projects into the Research Department workflow."""

    store: JsonStore

    def submit_idea(self, idea: str, approval_mode: str = "auto") -> dict[str, Any]:
        idea = " ".join(idea.strip().split())
        if not idea:
            raise ValueError("Founder idea cannot be empty")
        project = {"id": str(uuid4()), "idea": idea, "status": "CREATED"}
        self.store.save_project(project)
        LOGGER.info("project created", extra={"event": "project.created", "project_id": project["id"], "status": "CREATED"})
        engine = WorkflowEngine(self.store)
        workflow = engine.create(project["id"], "RESEARCH")
        LOGGER.info("orchestrator routed project", extra={"event": "orchestrator.routed", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RESEARCH"})

        department = ResearchDepartment(self.store)

        def run_research(current_workflow: dict[str, Any]) -> dict[str, Any]:
            return department.execute(project, current_workflow)

        completed_workflow = engine.run(workflow, run_research)
        if completed_workflow["status"] == "COMPLETED":
            project["status"] = "RESEARCH_COMPLETED"
            approval = ApprovalManager(self.store).request(project["id"], completed_workflow["id"], "PRODUCT_DEPARTMENT_ENTRY", mode=approval_mode)
            project["approvalId"] = approval["id"]
            project["approvalStatus"] = approval["status"]
            if approval["status"] == "PENDING":
                project["status"] = "AWAITING_APPROVAL"
        else:
            project["status"] = "RESEARCH_FAILED"
            approval = None
        project["workflowId"] = completed_workflow["id"]
        self.store.save_project(project)
        return {"project": project, "workflow": completed_workflow, "report": completed_workflow.get("result"), "approval": approval}

    def get_research_report(self, project_id: str) -> dict[str, Any]:
        return self.store.get_report(project_id)

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
            approvals = self.store.list_approvals(workflow_id=resumed_workflow["id"])
            approval = approvals[-1] if approvals else ApprovalManager(self.store).request(project["id"], resumed_workflow["id"], "PRODUCT_DEPARTMENT_ENTRY", mode=approval_mode)
            project["approvalId"] = approval["id"]
            project["approvalStatus"] = approval["status"]
            if approval["status"] == "PENDING":
                project["status"] = "AWAITING_APPROVAL"
        else:
            project["status"] = "RESEARCH_FAILED"
            approval = None
        project["workflowId"] = resumed_workflow["id"]
        self.store.save_project(project)
        return {"project": project, "workflow": resumed_workflow, "report": resumed_workflow.get("result"), "approval": approval}

    def approve_gate(self, approval_id: str, actor: str = "founder", note: str | None = None) -> dict[str, Any]:
        approval = ApprovalManager(self.store).approve(approval_id, actor=actor, note=note)
        project = self.store.get_project(approval["projectId"])
        project["approvalStatus"] = "APPROVED"
        if project.get("status") == "AWAITING_APPROVAL":
            project["status"] = "RESEARCH_APPROVED"
        self.store.save_project(project)
        return {"project": project, "approval": approval}

    def reject_gate(self, approval_id: str, actor: str = "founder", note: str | None = None) -> dict[str, Any]:
        approval = ApprovalManager(self.store).reject(approval_id, actor=actor, note=note)
        project = self.store.get_project(approval["projectId"])
        project["approvalStatus"] = "REJECTED"
        project["status"] = "RESEARCH_REJECTED"
        self.store.save_project(project)
        return {"project": project, "approval": approval}

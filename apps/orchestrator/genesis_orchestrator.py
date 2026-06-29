"""Genesis Orchestrator for Sprint 2 vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any
from uuid import uuid4

from apps.research import ResearchDepartment
from apps.storage import JsonStore
from apps.workflow import WorkflowEngine

LOGGER = logging.getLogger("genesis.orchestrator")


@dataclass
class GenesisOrchestrator:
    """Routes founder projects into the Research Department workflow."""

    store: JsonStore

    def submit_idea(self, idea: str) -> dict[str, Any]:
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
        else:
            project["status"] = "RESEARCH_FAILED"
        project["workflowId"] = completed_workflow["id"]
        self.store.save_project(project)
        return {"project": project, "workflow": completed_workflow, "report": completed_workflow.get("result")}

    def get_research_report(self, project_id: str) -> dict[str, Any]:
        return self.store.get_report(project_id)

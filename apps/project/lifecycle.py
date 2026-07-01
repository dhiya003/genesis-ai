"""Project lifecycle, governance, dashboard, and readiness runtime."""

from __future__ import annotations

from statistics import mean
from typing import Any
from uuid import uuid4

from apps.audit import now_iso, record_audit
from apps.storage import JsonStore

PROJECT_EDITABLE_FIELDS = {"title", "name", "description", "targetMarket", "timeline", "budgetAllocation", "priority", "status", "preferences", "constraints"}
VALID_PROJECT_STATUSES = {
    "DRAFT",
    "CREATED",
    "ACTIVE",
    "PLANNING",
    "RESEARCH",
    "RESEARCH_COMPLETED",
    "AWAITING_APPROVAL",
    "RESEARCH_APPROVED",
    "RESEARCH_FAILED",
    "PRODUCT_DEVELOPMENT",
    "PRODUCT_DEFINITION_COMPLETED",
    "PRODUCT_BLUEPRINT_COMPLETED",
    "CREATIVE",
    "CREATIVE_PACK_COMPLETED",
    "MARKETING",
    "MARKETING_PACK_COMPLETED",
    "PUBLISHING",
    "BUSINESS_LAUNCH_PACKAGE_COMPLETED",
    "MONITORING",
    "BUSINESS_OPERATING_PLAN_COMPLETED",
    "COMPLETED",
    "ARCHIVED",
    "CANCELLED",
    "WORKFLOW_WAITING",
    "WORKFLOW_CANCELLED",
}
TERMINAL_STATUSES = {"ARCHIVED", "CANCELLED", "COMPLETED"}


class ProjectLifecycleRuntime:
    """Manages the project layer between founder context and AI workflows."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def dashboard(self, project_id: str) -> dict[str, Any]:
        project = self.store.get_project(project_id)
        workflows = [workflow for workflow in self.store.list_workflows() if workflow.get("projectId") == project_id]
        tasks = self.store.list_tasks(project_id=project_id)
        deliverables = self.store.list_deliverables(project_id=project_id)
        approvals = self.store.list_approvals(project_id=project_id)
        audit_logs = self.store.list_audit_logs(project_id=project_id)
        health = self.health(project_id)["health"]
        timeline = self.timeline(project_id)["timeline"]
        active_workflows = [workflow for workflow in workflows if workflow.get("status") not in {"COMPLETED", "FAILED", "CANCELLED", "ARCHIVED"}]
        pending_approvals = [approval for approval in approvals if approval.get("status") == "PENDING"]
        return {
            "reportType": "PROJECT_DASHBOARD",
            "project": project,
            "projectName": project.get("title") or project.get("name") or project.get("idea"),
            "currentPhase": _current_phase(project),
            "completionPercent": _completion_percent(project, workflows, deliverables),
            "activeWorkflow": active_workflows[-1] if active_workflows else workflows[-1] if workflows else None,
            "workflowStatus": workflows[-1]["status"] if workflows else "NONE",
            "assignedDepartments": _assigned_departments(workflows, tasks),
            "pendingApprovals": pending_approvals,
            "businessHealth": health,
            "recentActivities": timeline[-10:],
            "deliverables": deliverables,
            "risks": _project_risks(project, workflows, pending_approvals),
            "recommendations": _project_recommendations(project, health, pending_approvals),
            "timeline": timeline,
            "kpis": _project_kpis(project, workflows, tasks, deliverables, approvals),
            "refreshMode": "on_demand",
            "refreshedAt": now_iso(),
            "auditLogs": audit_logs,
            "implementedExtrasForReview": {
                "productKnowledge": self.store.list_product_knowledge(project_id=project_id),
                "executionHistory": self.store.list_execution_history(project_id=project_id),
            },
        }

    def update(self, project_id: str, payload: dict[str, Any], *, actor: str = "founder") -> dict[str, Any]:
        project = self.store.get_project(project_id)
        self._save_project_version(project, actor=actor, reason="before_update")
        changed: dict[str, Any] = {}
        for key, value in payload.items():
            if key not in PROJECT_EDITABLE_FIELDS:
                continue
            target_key = "title" if key == "name" else key
            if target_key == "status":
                next_status = _status(value)
                self._assert_transition(project.get("status", "DRAFT"), next_status)
                value = next_status
            if target_key == "priority" and str(value).upper() not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
                raise ValueError("priority must be LOW, MEDIUM, HIGH, or CRITICAL")
            project[target_key] = value
            changed[target_key] = value
        if not changed:
            raise ValueError("No editable project fields supplied")
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        self._save_project_version(project, actor=actor, reason="after_update")
        record_audit(self.store, "project.updated", actor=actor, project_id=project_id, details={"changedFields": sorted(changed)})
        return {"project": project, "changedFields": sorted(changed), "versions": self.store.list_project_versions(project_id)}

    def archive(self, project_id: str, *, actor: str = "founder", reason: str = "archived by founder") -> dict[str, Any]:
        project = self.store.get_project(project_id)
        if project.get("status") == "ARCHIVED":
            return {"project": project, "idempotent": True}
        project["previousStatus"] = project.get("status", "ACTIVE")
        project["status"] = "ARCHIVED"
        project["archivedAt"] = now_iso()
        project["archiveReason"] = reason
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        self._save_project_version(project, actor=actor, reason="archived")
        record_audit(self.store, "project.archived", actor=actor, project_id=project_id, details={"reason": reason})
        return {"project": project, "timeline": self.timeline(project_id)["timeline"]}

    def restore(self, project_id: str, *, actor: str = "founder") -> dict[str, Any]:
        project = self.store.get_project(project_id)
        if project.get("status") != "ARCHIVED":
            raise ValueError("Only ARCHIVED projects can be restored")
        project["status"] = "ACTIVE"
        project["restoredAt"] = now_iso()
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        self._save_project_version(project, actor=actor, reason="restored")
        record_audit(self.store, "project.restored", actor=actor, project_id=project_id, details={"restoredTo": "ACTIVE"})
        return {"project": project, "timeline": self.timeline(project_id)["timeline"]}

    def duplicate(self, project_id: str, *, actor: str = "founder", title: str | None = None) -> dict[str, Any]:
        original = self.store.get_project(project_id)
        timestamp = now_iso()
        copy_fields = ["businessId", "description", "targetMarket", "timeline", "budgetAllocation", "priority", "preferences", "constraints", "inheritedConstraints", "founderProfileSnapshot", "visionSnapshot", "owner"]
        duplicate = {key: original[key] for key in copy_fields if key in original}
        duplicate.update(
            {
                "id": str(uuid4()),
                "title": title or f"Copy of {original.get('title') or original.get('name') or original.get('idea', 'Project')}",
                "sourceProjectId": project_id,
                "status": "DRAFT",
                "createdAt": timestamp,
                "updatedAt": timestamp,
                "duplicatedBy": actor,
            }
        )
        self.store.save_project(duplicate)
        self._save_project_version(duplicate, actor=actor, reason="duplicated")
        record_audit(self.store, "project.duplicated", actor=actor, project_id=duplicate["id"], details={"sourceProjectId": project_id})
        return {"project": duplicate, "sourceProject": original}

    def timeline(self, project_id: str, *, event_type: str | None = None) -> dict[str, Any]:
        self.store.get_project(project_id)
        items: list[dict[str, Any]] = []
        for log in self.store.list_audit_logs(project_id=project_id):
            items.append(
                {
                    "id": log["id"],
                    "type": log.get("eventType") or log.get("event"),
                    "source": "audit",
                    "timestamp": log["createdAt"],
                    "actor": log.get("actor") or "system",
                    "details": log.get("details", {}),
                    "immutable": True,
                }
            )
        for event in self.store.list_execution_history(project_id=project_id):
            items.append(
                {
                    "id": event["id"],
                    "type": event.get("eventType") or event.get("event"),
                    "source": "execution_history",
                    "timestamp": event["createdAt"],
                    "actor": event.get("actor") or "system",
                    "workflowId": event.get("workflowId"),
                    "status": event.get("status"),
                    "details": event.get("details", {}),
                    "immutable": True,
                }
            )
        items.sort(key=lambda item: str(item.get("timestamp", "")))
        if event_type:
            items = [item for item in items if item.get("type") == event_type or item.get("source") == event_type]
        return {"projectId": project_id, "filters": {"eventType": event_type}, "timeline": items, "export": {"format": "json", "itemCount": len(items)}}

    def health(self, project_id: str) -> dict[str, Any]:
        project = self.store.get_project(project_id)
        workflows = [workflow for workflow in self.store.list_workflows() if workflow.get("projectId") == project_id]
        deliverables = self.store.list_deliverables(project_id=project_id)
        approvals = self.store.list_approvals(project_id=project_id)
        factors = _health_factors(project, workflows, deliverables, approvals)
        score = round(mean(factors.values())) if factors else 0
        previous = self.store.list_project_health(project_id)
        trend = "STABLE"
        if previous:
            previous_score = int(previous[-1]["health"]["score"])
            if score > previous_score:
                trend = "IMPROVING"
            elif score < previous_score:
                trend = "DECLINING"
        health = {"projectId": project_id, "score": max(0, min(100, score)), "status": "LOW" if score < 60 else "WATCH" if score < 80 else "HEALTHY", "factors": factors, "trend": trend, "calculatedAt": now_iso()}
        self.store.save_project_health({"id": str(uuid4()), "projectId": project_id, "health": health, "createdAt": now_iso()})
        return {"health": health, "history": self.store.list_project_health(project_id)}

    def validate_readiness(self, project_id: str, *, actor: str = "founder") -> dict[str, Any]:
        project = self.store.get_project(project_id)
        checks = []
        business = None
        business_id = project.get("businessId")
        if business_id:
            try:
                business = self.store.get_business(str(business_id))
                checks.append(_check("business_exists", True, "BLOCKING", "Business exists."))
                checks.append(_check("business_active", business.get("status") in {"ACTIVE", "DRAFT"}, "BLOCKING", "Business is active enough for planning."))
            except FileNotFoundError:
                checks.append(_check("business_exists", False, "BLOCKING", "Business record is missing."))
        else:
            checks.append(_check("business_exists", False, "BLOCKING", "Project is not linked to a business."))
        if business_id:
            checks.append(_check("vision_defined", self.store.get_active_business_vision(str(business_id)) is not None, "BLOCKING", "Business vision is defined."))
            checks.append(_check("goals_defined", bool(self.store.list_business_goals(str(business_id))), "BLOCKING", "Business goals are defined."))
            checks.append(_check("constraints_defined", bool(self.store.list_business_constraints(str(business_id))), "BLOCKING", "Business constraints are defined."))
            checks.append(_check("budget_configured", _exists(lambda: self.store.get_business_budget(str(business_id))), "WARNING", "Budget is configured."))
            checks.append(_check("approval_policy_configured", _exists(lambda: self.store.get_business_approval_policy(str(business_id))), "WARNING", "Approval policy is configured."))
        founder_profile = _exists(lambda: self.store.get_founder_profile(str(project.get("owner", "founder"))))
        checks.append(_check("founder_profile_completed", founder_profile, "WARNING", "Founder profile is completed."))
        checks.append(_check("project_status_valid", project.get("status") in VALID_PROJECT_STATUSES, "BLOCKING", "Project status is valid."))
        checks.append(_check("required_project_fields_completed", bool(project.get("title") or project.get("name") or project.get("idea")), "BLOCKING", "Project title/name exists."))
        blocking_failures = [check for check in checks if not check["passed"] and check["severity"] == "BLOCKING"]
        warnings = [check for check in checks if not check["passed"] and check["severity"] == "WARNING"]
        outcome = "BLOCKED" if blocking_failures else "READY_WITH_WARNINGS" if warnings else "READY"
        report = {"id": str(uuid4()), "projectId": project_id, "outcome": outcome, "checks": checks, "blockingErrors": blocking_failures, "warnings": warnings, "createdAt": now_iso(), "createdBy": actor}
        self.store.save_project_readiness(report)
        record_audit(self.store, "project.readiness_validated", actor=actor, project_id=project_id, details={"outcome": outcome, "blockingErrors": len(blocking_failures), "warnings": len(warnings)})
        return {"readiness": report}

    def _save_project_version(self, project: dict[str, Any], *, actor: str, reason: str) -> None:
        versions = self.store.list_project_versions(project["id"])
        snapshot = dict(project)
        snapshot["version"] = len(versions) + 1
        snapshot["snapshotAt"] = now_iso()
        snapshot["snapshotBy"] = actor
        snapshot["snapshotReason"] = reason
        self.store.save_project_version(snapshot)

    def _assert_transition(self, current: str, next_status: str) -> None:
        current = _status(current)
        if current == next_status:
            return
        if current in TERMINAL_STATUSES and next_status not in {"ACTIVE", "ARCHIVED"}:
            raise ValueError(f"Cannot transition project from {current} to {next_status}")
        if next_status not in VALID_PROJECT_STATUSES:
            raise ValueError(f"Invalid project status: {next_status}")


def _status(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_")


def _check(name: str, passed: bool, severity: str, message: str) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "severity": severity, "message": message}


def _exists(fn: Any) -> bool:
    try:
        fn()
        return True
    except FileNotFoundError:
        return False


def _current_phase(project: dict[str, Any]) -> str:
    status = str(project.get("status", "DRAFT"))
    if "PRODUCT" in status:
        return "Product Development"
    if "CREATIVE" in status:
        return "Creative"
    if "MARKETING" in status:
        return "Marketing"
    if "LAUNCH" in status or "PUBLISHING" in status:
        return "Publishing"
    if "OPERATING" in status or "MONITORING" in status:
        return "Monitoring"
    if "RESEARCH" in status:
        return "Research"
    return status.replace("_", " ").title()


def _completion_percent(project: dict[str, Any], workflows: list[dict[str, Any]], deliverables: list[dict[str, Any]]) -> int:
    if project.get("status") == "COMPLETED":
        return 100
    completed_workflows = len([workflow for workflow in workflows if workflow.get("status") == "COMPLETED"])
    failed_workflows = len([workflow for workflow in workflows if workflow.get("status") in {"FAILED", "CANCELLED"}])
    base = min(90, completed_workflows * 15 + len(deliverables) * 5)
    return max(0, base - failed_workflows * 10)


def _assigned_departments(workflows: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> list[str]:
    departments = {str(workflow.get("scheduledDepartment")) for workflow in workflows if workflow.get("scheduledDepartment")}
    departments.update(str(task.get("type")) for task in tasks if task.get("type"))
    return sorted(departments)


def _project_risks(project: dict[str, Any], workflows: list[dict[str, Any]], pending_approvals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risks = []
    if any(workflow.get("status") == "FAILED" for workflow in workflows):
        risks.append({"severity": "HIGH", "risk": "Workflow failure requires retry or review."})
    if pending_approvals:
        risks.append({"severity": "MEDIUM", "risk": "Pending founder approval is blocking next-stage execution."})
    if project.get("status") == "ARCHIVED":
        risks.append({"severity": "LOW", "risk": "Project is archived and excluded from active execution."})
    return risks


def _project_recommendations(project: dict[str, Any], health: dict[str, Any], pending_approvals: list[dict[str, Any]]) -> list[str]:
    recommendations = []
    if pending_approvals:
        recommendations.append("Review pending approvals before starting downstream departments.")
    if health["score"] < 80:
        recommendations.append("Inspect low-scoring health factors and resolve blockers before scaling execution.")
    if project.get("status") == "DRAFT":
        recommendations.append("Run readiness validation and start planning when business context is complete.")
    return recommendations or ["Continue current execution plan."]


def _project_kpis(project: dict[str, Any], workflows: list[dict[str, Any]], tasks: list[dict[str, Any]], deliverables: list[dict[str, Any]], approvals: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "workflowCount": len(workflows),
        "completedWorkflowCount": len([workflow for workflow in workflows if workflow.get("status") == "COMPLETED"]),
        "taskCount": len(tasks),
        "completedTaskCount": len([task for task in tasks if task.get("status") == "COMPLETED"]),
        "deliverableCount": len(deliverables),
        "pendingApprovalCount": len([approval for approval in approvals if approval.get("status") == "PENDING"]),
        "priority": project.get("priority", "MEDIUM"),
    }


def _health_factors(project: dict[str, Any], workflows: list[dict[str, Any]], deliverables: list[dict[str, Any]], approvals: list[dict[str, Any]]) -> dict[str, int]:
    failed = len([workflow for workflow in workflows if workflow.get("status") == "FAILED"])
    completed = len([workflow for workflow in workflows if workflow.get("status") == "COMPLETED"])
    pending = len([approval for approval in approvals if approval.get("status") == "PENDING"])
    return {
        "researchQuality": 90 if project.get("workflowId") or any(workflow.get("type") == "RESEARCH" for workflow in workflows) else 60,
        "timeline": 80 if project.get("timeline") else 65,
        "budget": 80 if project.get("budget") or project.get("budgetAllocation") else 65,
        "risk": max(30, 90 - failed * 25 - pending * 10),
        "deliverables": min(100, 60 + len(deliverables) * 10),
        "workflowSuccess": min(100, 70 + completed * 10 - failed * 20),
        "pendingIssues": max(40, 100 - pending * 15 - failed * 25),
        "approvals": max(50, 95 - pending * 15),
    }

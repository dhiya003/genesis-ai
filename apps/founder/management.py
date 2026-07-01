"""Founder Experience runtime for Genesis v1 Epic 01."""

from __future__ import annotations

from statistics import mean
from typing import Any
from uuid import uuid4

from apps.audit import now_iso, record_audit
from apps.storage import JsonStore
from apps.workflow import WorkflowEngine

DEFAULT_FOUNDER_ID = "founder"
BUSINESS_REQUIRED_FIELDS = ["name", "country", "currency", "primaryMarket"]
PROFILE_FIELDS = ["name", "language", "timeZone", "currency", "riskAppetite", "budgetPreference", "experienceLevel", "communicationStyle", "workingHours", "approvalPolicy"]
VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


class FounderBusinessRuntime:
    """Creates and manages first-class business context before department work."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def create_business(self, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID, idempotency_key: str | None = None, draft: bool = False) -> dict[str, Any]:
        effective_key = idempotency_key or _text(payload.get("idempotencyKey"))
        if effective_key:
            existing = self.store.find_business_by_idempotency_key(founder_id, effective_key)
            if existing:
                return {"business": existing, "dashboard": self.business_dashboard(existing["id"]), "idempotent": True}

        name = _required(payload, "name", "Business Name")
        country = _required(payload, "country", "Country")
        currency = _required(payload, "currency", "Currency")
        primary_market = _required(payload, "primaryMarket", "Primary Market")
        timestamp = now_iso()
        business = {
            "id": str(uuid4()),
            "name": name,
            "industry": _text(payload.get("industry")),
            "country": country,
            "currency": currency,
            "primaryMarket": primary_market,
            "status": "DRAFT" if draft else "ACTIVE",
            "creator": founder_id,
            "founderId": founder_id,
            "idempotencyKey": effective_key,
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }
        self.store.save_business(business)
        record_audit(self.store, "business.created", actor=founder_id, project_id=business["id"], details={"businessId": business["id"], "status": business["status"], "name": name})
        return {"business": business, "dashboard": self.business_dashboard(business["id"]), "idempotent": False}

    def list_businesses(self, *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        return {"founderId": founder_id, "businesses": self.store.list_businesses(founder_id=founder_id)}

    def business_dashboard(self, business_id: str) -> dict[str, Any]:
        business = self.store.get_business(business_id)
        projects = self.store.list_projects(business_id=business_id)
        vision = self.store.get_active_business_vision(business_id)
        goals = self.store.list_business_goals(business_id)
        constraints = self.store.list_business_constraints(business_id)
        budget = _optional(lambda: self.store.get_business_budget(business_id), default={"businessId": business_id, "categories": [], "totalAllocated": 0, "totalSpent": 0, "remainingBudget": 0, "currency": business.get("currency")})
        success_metrics = self.store.list_business_success_metrics(business_id)
        approval_policy = _optional(lambda: self.store.get_business_approval_policy(business_id), default={"businessId": business_id, "rules": [], "approvalHistory": []})
        return {
            "reportType": "BUSINESS_DASHBOARD",
            "business": business,
            "activeVision": vision,
            "goals": goals,
            "constraints": constraints,
            "budget": budget,
            "successMetrics": _with_progress(success_metrics),
            "approvalPolicy": approval_policy,
            "projects": projects,
            "auditLogs": _business_audit_logs(self.store, business_id),
            "planningReadiness": self._planning_readiness(business_id),
        }

    def upsert_founder_profile(self, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        profile_payload = {field: payload.get(field) for field in PROFILE_FIELDS if field in payload}
        if not profile_payload.get("name"):
            raise ValueError("Name is required")
        previous = _optional(lambda: self.store.get_founder_profile(founder_id), default=None)
        version_number = int(previous.get("version", 0)) + 1 if isinstance(previous, dict) else 1
        timestamp = now_iso()
        profile = {
            "founderId": founder_id,
            "version": version_number,
            "createdAt": previous.get("createdAt", timestamp) if isinstance(previous, dict) else timestamp,
            "updatedAt": timestamp,
            **profile_payload,
        }
        version = dict(profile)
        version["snapshotAt"] = timestamp
        self.store.save_founder_profile(profile)
        self.store.save_founder_profile_version(version)
        record_audit(self.store, "founder_profile.updated", actor=founder_id, details={"founderId": founder_id, "version": version_number})
        return {"profile": profile, "versions": self.store.list_founder_profile_versions(founder_id)}

    def get_founder_profile(self, *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        return {"profile": self.store.get_founder_profile(founder_id), "versions": self.store.list_founder_profile_versions(founder_id)}

    def set_business_vision(self, business_id: str, content: str, *, founder_id: str = DEFAULT_FOUNDER_ID, content_format: str = "markdown") -> dict[str, Any]:
        self.store.get_business(business_id)
        content = " ".join(content.strip().split())
        if not content:
            raise ValueError("Vision content is required")
        existing_versions = self.store.list_business_vision_versions(business_id)
        for version in existing_versions:
            version["status"] = "SUPERSEDED"
            self.store.save_business_vision_version(version)
        version_number = len(existing_versions) + 1
        timestamp = now_iso()
        vision = {
            "id": str(uuid4()),
            "businessId": business_id,
            "version": version_number,
            "content": content,
            "contentFormat": content_format,
            "status": "ACTIVE",
            "createdBy": founder_id,
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }
        self.store.save_business_vision_version(vision)
        record_audit(self.store, "business_vision.updated", actor=founder_id, project_id=business_id, details={"businessId": business_id, "version": version_number})
        return {"activeVision": vision, "versions": self.store.list_business_vision_versions(business_id)}

    def add_business_goal(self, business_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        self.store.get_business(business_id)
        goal = {
            "id": str(uuid4()),
            "businessId": business_id,
            "type": _required(payload, "type", "Goal Type"),
            "targetValue": _number(payload.get("targetValue"), "Target value"),
            "unit": _text(payload.get("unit")),
            "targetDate": _required(payload, "targetDate", "Target date"),
            "priority": _priority(payload.get("priority", "MEDIUM")),
            "status": "ACTIVE",
            "createdBy": founder_id,
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }
        self.store.save_business_goal(goal)
        record_audit(self.store, "business_goal.created", actor=founder_id, project_id=business_id, details={"businessId": business_id, "goalId": goal["id"]})
        return {"goal": goal, "goals": self.store.list_business_goals(business_id)}

    def update_business_goal(self, business_id: str, goal_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        goal = self.store.get_business_goal(business_id, goal_id)
        for key in ["type", "unit", "targetDate"]:
            if key in payload:
                goal[key] = _required(payload, key, key)
        if "targetValue" in payload:
            goal["targetValue"] = _number(payload.get("targetValue"), "Target value")
        if "priority" in payload:
            goal["priority"] = _priority(payload.get("priority"))
        if payload.get("archive") is True:
            goal["status"] = "ARCHIVED"
        goal["updatedAt"] = now_iso()
        self.store.save_business_goal(goal)
        record_audit(self.store, "business_goal.updated", actor=founder_id, project_id=business_id, details={"businessId": business_id, "goalId": goal_id, "status": goal["status"]})
        return {"goal": goal, "goals": self.store.list_business_goals(business_id, include_archived=True)}

    def add_business_constraint(self, business_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        self.store.get_business(business_id)
        timestamp = now_iso()
        constraint = {
            "id": str(uuid4()),
            "businessId": business_id,
            "version": 1,
            "type": _required(payload, "type", "Constraint type"),
            "description": _required(payload, "description", "Constraint description"),
            "status": "ACTIVE",
            "createdBy": founder_id,
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }
        self.store.save_business_constraint_version(constraint)
        record_audit(self.store, "business_constraint.created", actor=founder_id, project_id=business_id, details={"businessId": business_id, "constraintId": constraint["id"], "version": 1})
        return {"constraint": constraint, "constraints": self.store.list_business_constraints(business_id)}

    def update_business_constraint(self, business_id: str, constraint_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        versions = self.store.list_business_constraint_versions(business_id, constraint_id)
        if not versions:
            raise FileNotFoundError(f"Constraint not found: {constraint_id}")
        latest = versions[-1]
        next_version = dict(latest)
        next_version["version"] = int(latest["version"]) + 1
        if "type" in payload:
            next_version["type"] = _required(payload, "type", "Constraint type")
        if "description" in payload:
            next_version["description"] = _required(payload, "description", "Constraint description")
        if payload.get("archive") is True:
            next_version["status"] = "ARCHIVED"
        next_version["updatedAt"] = now_iso()
        next_version["createdBy"] = founder_id
        self.store.save_business_constraint_version(next_version)
        record_audit(self.store, "business_constraint.updated", actor=founder_id, project_id=business_id, details={"businessId": business_id, "constraintId": constraint_id, "version": next_version["version"]})
        return {"constraint": next_version, "versions": self.store.list_business_constraint_versions(business_id, constraint_id), "constraints": self.store.list_business_constraints(business_id, include_archived=True)}

    def set_business_budget(self, business_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        business = self.store.get_business(business_id)
        currency = _text(payload.get("currency")) or business.get("currency")
        categories = payload.get("categories")
        if not isinstance(categories, list) or not categories:
            raise ValueError("Budget categories are required")
        normalized = []
        for category in categories:
            if not isinstance(category, dict):
                raise ValueError("Each budget category must be an object")
            allocated = _number(category.get("allocated"), "Allocated budget")
            spent = _number(category.get("spent", 0), "Spent budget")
            normalized.append({"category": _required(category, "category", "Budget category"), "allocated": allocated, "spent": spent, "remaining": round(allocated - spent, 2)})
        total_allocated = round(sum(item["allocated"] for item in normalized), 2)
        total_spent = round(sum(item["spent"] for item in normalized), 2)
        budget = {
            "businessId": business_id,
            "currency": currency,
            "categories": normalized,
            "totalAllocated": total_allocated,
            "totalSpent": total_spent,
            "remainingBudget": round(total_allocated - total_spent, 2),
            "updatedBy": founder_id,
            "updatedAt": now_iso(),
        }
        self.store.save_business_budget(budget)
        record_audit(self.store, "business_budget.updated", actor=founder_id, project_id=business_id, details={"businessId": business_id, "remainingBudget": budget["remainingBudget"]})
        return {"budget": budget}

    def add_success_metric(self, business_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        self.store.get_business(business_id)
        metric = {
            "id": str(uuid4()),
            "businessId": business_id,
            "name": _required(payload, "name", "Metric name"),
            "unit": _required(payload, "unit", "Metric unit"),
            "targetValue": _number(payload.get("targetValue"), "Target value"),
            "currentValue": _number(payload.get("currentValue", 0), "Current value"),
            "timeHorizon": _required(payload, "timeHorizon", "Time horizon"),
            "createdBy": founder_id,
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }
        self.store.save_business_success_metric(metric)
        record_audit(self.store, "business_success_metric.created", actor=founder_id, project_id=business_id, details={"businessId": business_id, "metricId": metric["id"]})
        return {"metric": _with_progress([metric])[0], "metrics": _with_progress(self.store.list_business_success_metrics(business_id))}

    def set_approval_policy(self, business_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        self.store.get_business(business_id)
        rules = payload.get("rules")
        if not isinstance(rules, list):
            raise ValueError("Approval rules must be a list")
        normalized = []
        for rule in rules:
            if not isinstance(rule, dict):
                raise ValueError("Each approval rule must be an object")
            normalized.append(
                {
                    "type": _required(rule, "type", "Approval type"),
                    "mode": _required(rule, "mode", "Approval mode").upper(),
                    "budgetThreshold": _number(rule.get("budgetThreshold", 0), "Budget threshold"),
                    "condition": _text(rule.get("condition")),
                }
            )
        existing = _optional(lambda: self.store.get_business_approval_policy(business_id), default={"approvalHistory": []})
        history = list(existing.get("approvalHistory", []))
        history.append({"changedAt": now_iso(), "changedBy": founder_id, "ruleCount": len(normalized)})
        policy = {"businessId": business_id, "rules": normalized, "approvalHistory": history, "updatedAt": now_iso(), "updatedBy": founder_id}
        self.store.save_business_approval_policy(policy)
        record_audit(self.store, "business_approval_policy.updated", actor=founder_id, project_id=business_id, details={"businessId": business_id, "ruleCount": len(normalized)})
        return {"approvalPolicy": policy}

    def create_project(self, business_id: str, payload: dict[str, Any], *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        self.store.get_business(business_id)
        timestamp = now_iso()
        project = {
            "id": str(uuid4()),
            "businessId": business_id,
            "title": _required(payload, "title", "Project title"),
            "description": _text(payload.get("description")),
            "owner": founder_id,
            "status": "DRAFT",
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "inheritedConstraints": self.store.list_business_constraints(business_id),
            "founderProfileSnapshot": _optional(lambda: self.store.get_founder_profile(founder_id), default=None),
            "visionSnapshot": self.store.get_active_business_vision(business_id),
        }
        self.store.save_project(project)
        record_audit(self.store, "business_project.created", actor=founder_id, project_id=project["id"], details={"businessId": business_id, "projectId": project["id"]})
        return {"project": project, "dashboard": self.business_dashboard(business_id)}

    def start_project_planning(self, business_id: str, project_id: str, *, founder_id: str = DEFAULT_FOUNDER_ID) -> dict[str, Any]:
        self.store.get_business(business_id)
        project = self.store.get_project(project_id)
        if project.get("businessId") != business_id:
            raise ValueError("Project does not belong to business")
        readiness = self._planning_readiness(business_id)
        if not readiness["ready"]:
            raise ValueError(f"Planning cannot start: {', '.join(readiness['missing'])}")
        workflow = WorkflowEngine(self.store).create(project_id, "PROJECT_PLANNING")
        workflow = WorkflowEngine(self.store).plan(workflow, reason="founder started business project planning")
        workflow["scheduledDepartment"] = "RESEARCH_DEPARTMENT"
        workflow["businessContext"] = {
            "business": self.store.get_business(business_id),
            "vision": self.store.get_active_business_vision(business_id),
            "goals": self.store.list_business_goals(business_id),
            "constraints": self.store.list_business_constraints(business_id),
            "budget": _optional(lambda: self.store.get_business_budget(business_id), default=None),
            "founderProfileSnapshot": _optional(lambda: self.store.get_founder_profile(founder_id), default=None),
        }
        self.store.save_workflow(workflow)
        project["status"] = "PLANNING"
        project["planningWorkflowId"] = workflow["id"]
        project["updatedAt"] = now_iso()
        self.store.save_project(project)
        record_audit(self.store, "business_project.planning_started", actor=founder_id, project_id=project_id, workflow_id=workflow["id"], details={"businessId": business_id})
        return {"project": project, "workflow": workflow, "dashboard": self.business_dashboard(business_id)}

    def _planning_readiness(self, business_id: str) -> dict[str, Any]:
        missing = []
        if self.store.get_active_business_vision(business_id) is None:
            missing.append("vision")
        if not self.store.list_business_goals(business_id):
            missing.append("goals")
        if not self.store.list_business_constraints(business_id):
            missing.append("constraints")
        return {"ready": not missing, "missing": missing}


def _required(payload: dict[str, Any], key: str, label: str) -> str:
    value = _text(payload.get(key))
    if not value:
        raise ValueError(f"{label} is required")
    return value


def _text(value: Any) -> str:
    return " ".join(str(value).strip().split()) if value is not None else ""


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a number")
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    try:
        return round(float(str(value).strip()), 2)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc


def _priority(value: Any) -> str:
    priority = _text(value).upper() or "MEDIUM"
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be one of {sorted(VALID_PRIORITIES)}")
    return priority


def _optional(fn: Any, *, default: Any) -> Any:
    try:
        return fn()
    except FileNotFoundError:
        return default


def _with_progress(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    for metric in metrics:
        item = dict(metric)
        target = item.get("targetValue", 0)
        current = item.get("currentValue", 0)
        item["progressPercent"] = round(min(100, (float(current) / float(target)) * 100), 2) if target else 0
        enriched.append(item)
    return enriched


def _business_audit_logs(store: JsonStore, business_id: str) -> list[dict[str, Any]]:
    logs = [
        log
        for log in store.list_audit_logs()
        if log.get("projectId") == business_id or log.get("details", {}).get("businessId") == business_id
    ]
    logs.sort(key=lambda item: str(item.get("createdAt", "")))
    return logs


def business_goal_score(goals: list[dict[str, Any]]) -> int:
    if not goals:
        return 0
    priority_weights = {"LOW": 40, "MEDIUM": 60, "HIGH": 80, "CRITICAL": 100}
    return round(mean(priority_weights.get(goal.get("priority", "MEDIUM"), 60) for goal in goals))

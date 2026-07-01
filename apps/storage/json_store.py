"""File-backed JSON persistence for the Sprint 2 vertical slice."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStore:
    """Small deterministic JSON store used by local API, CLI, and tests."""

    def __init__(self, root: str | Path = ".genesis-data") -> None:
        self.root = Path(root)
        self.businesses_dir = self.root / "businesses"
        self.founder_profiles_dir = self.root / "founder_profiles"
        self.founder_profile_versions_dir = self.root / "founder_profile_versions"
        self.business_visions_dir = self.root / "business_visions"
        self.business_goals_dir = self.root / "business_goals"
        self.business_constraints_dir = self.root / "business_constraints"
        self.business_budgets_dir = self.root / "business_budgets"
        self.business_success_metrics_dir = self.root / "business_success_metrics"
        self.business_approval_policies_dir = self.root / "business_approval_policies"
        self.projects_dir = self.root / "projects"
        self.workflows_dir = self.root / "workflows"
        self.employee_outputs_dir = self.root / "employee_outputs"
        self.reports_dir = self.root / "reports"
        self.approvals_dir = self.root / "approvals"
        self.metrics_dir = self.root / "metrics"
        self.tasks_dir = self.root / "tasks"
        self.deliverables_dir = self.root / "deliverables"
        self.audit_logs_dir = self.root / "audit_logs"
        self.execution_history_dir = self.root / "execution_history"
        self.product_definitions_dir = self.root / "product_definitions"
        self.product_blueprints_dir = self.root / "product_blueprints"
        self.product_knowledge_dir = self.root / "product_knowledge"
        self.bom_reports_dir = self.root / "bom_reports"
        self.cost_reports_dir = self.root / "cost_reports"
        self.supplier_reports_dir = self.root / "supplier_reports"
        self.packaging_reports_dir = self.root / "packaging_reports"
        self.profitability_reports_dir = self.root / "profitability_reports"
        self.manufacturing_plans_dir = self.root / "manufacturing_plans"
        self.creative_packs_dir = self.root / "creative_packs"
        self.creative_assets_dir = self.root / "creative_assets"
        self.brand_reports_dir = self.root / "brand_reports"
        self.logo_reports_dir = self.root / "logo_reports"
        self.creative_packaging_reports_dir = self.root / "creative_packaging_reports"
        self.mockup_reports_dir = self.root / "mockup_reports"
        self.marketplace_creative_reports_dir = self.root / "marketplace_creative_reports"
        self.social_creative_reports_dir = self.root / "social_creative_reports"
        self.copy_reports_dir = self.root / "copy_reports"
        self.marketing_packs_dir = self.root / "marketing_packs"
        self.marketing_strategy_reports_dir = self.root / "marketing_strategy_reports"
        self.seo_reports_dir = self.root / "seo_reports"
        self.social_marketing_reports_dir = self.root / "social_marketing_reports"
        self.ads_reports_dir = self.root / "ads_reports"
        self.listing_reports_dir = self.root / "listing_reports"
        self.launch_reports_dir = self.root / "launch_reports"
        self.business_launch_packages_dir = self.root / "business_launch_packages"
        self.business_launch_checklists_dir = self.root / "business_launch_checklists"
        self.publishing_plans_dir = self.root / "publishing_plans"
        self.asset_manifests_dir = self.root / "asset_manifests"
        self.business_launch_reports_dir = self.root / "business_launch_reports"
        self.business_operating_plans_dir = self.root / "business_operating_plans"
        self.digital_twins_dir = self.root / "digital_twins"
        self.knowledge_graphs_dir = self.root / "knowledge_graphs"
        self.decision_registers_dir = self.root / "decision_registers"
        self.simulation_reports_dir = self.root / "simulation_reports"
        self.business_health_reports_dir = self.root / "business_health_reports"
        self.recommendation_reports_dir = self.root / "recommendation_reports"
        self.business_metric_events_dir = self.root / "business_metric_events"
        self.business_dashboards_dir = self.root / "business_dashboards"
        self.business_alerts_dir = self.root / "business_alerts"
        self.business_knowledge_dir = self.root / "business_knowledge"
        for directory in [
            self.businesses_dir,
            self.founder_profiles_dir,
            self.founder_profile_versions_dir,
            self.business_visions_dir,
            self.business_goals_dir,
            self.business_constraints_dir,
            self.business_budgets_dir,
            self.business_success_metrics_dir,
            self.business_approval_policies_dir,
            self.projects_dir,
            self.workflows_dir,
            self.employee_outputs_dir,
            self.reports_dir,
            self.approvals_dir,
            self.metrics_dir,
            self.tasks_dir,
            self.deliverables_dir,
            self.audit_logs_dir,
            self.execution_history_dir,
            self.product_definitions_dir,
            self.product_blueprints_dir,
            self.product_knowledge_dir,
            self.bom_reports_dir,
            self.cost_reports_dir,
            self.supplier_reports_dir,
            self.packaging_reports_dir,
            self.profitability_reports_dir,
            self.manufacturing_plans_dir,
            self.creative_packs_dir,
            self.creative_assets_dir,
            self.brand_reports_dir,
            self.logo_reports_dir,
            self.creative_packaging_reports_dir,
            self.mockup_reports_dir,
            self.marketplace_creative_reports_dir,
            self.social_creative_reports_dir,
            self.copy_reports_dir,
            self.marketing_packs_dir,
            self.marketing_strategy_reports_dir,
            self.seo_reports_dir,
            self.social_marketing_reports_dir,
            self.ads_reports_dir,
            self.listing_reports_dir,
            self.launch_reports_dir,
            self.business_launch_packages_dir,
            self.business_launch_checklists_dir,
            self.publishing_plans_dir,
            self.asset_manifests_dir,
            self.business_launch_reports_dir,
            self.business_operating_plans_dir,
            self.digital_twins_dir,
            self.knowledge_graphs_dir,
            self.decision_registers_dir,
            self.simulation_reports_dir,
            self.business_health_reports_dir,
            self.recommendation_reports_dir,
            self.business_metric_events_dir,
            self.business_dashboards_dir,
            self.business_alerts_dir,
            self.business_knowledge_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def save_business(self, business: dict[str, Any]) -> None:
        self._write(self.businesses_dir / f"{business['id']}.json", business)

    def get_business(self, business_id: str) -> dict[str, Any]:
        return self._read(self.businesses_dir / f"{business_id}.json")

    def list_businesses(self, founder_id: str | None = None) -> list[dict[str, Any]]:
        businesses = [self._read(path) for path in sorted(self.businesses_dir.glob("*.json"))]
        if founder_id is not None:
            businesses = [business for business in businesses if business.get("creator") == founder_id or business.get("founderId") == founder_id]
        businesses.sort(key=lambda item: str(item.get("createdAt", "")))
        return businesses

    def find_business_by_idempotency_key(self, founder_id: str, idempotency_key: str) -> dict[str, Any] | None:
        for business in self.list_businesses(founder_id=founder_id):
            if business.get("idempotencyKey") == idempotency_key:
                return business
        return None

    def save_founder_profile(self, profile: dict[str, Any]) -> None:
        self._write(self.founder_profiles_dir / f"{profile['founderId']}.json", profile)

    def get_founder_profile(self, founder_id: str) -> dict[str, Any]:
        return self._read(self.founder_profiles_dir / f"{founder_id}.json")

    def save_founder_profile_version(self, version: dict[str, Any]) -> None:
        self._write(self.founder_profile_versions_dir / f"{version['founderId']}__{int(version['version']):04d}.json", version)

    def list_founder_profile_versions(self, founder_id: str) -> list[dict[str, Any]]:
        versions = [self._read(path) for path in sorted(self.founder_profile_versions_dir.glob(f"{founder_id}__*.json"))]
        versions.sort(key=lambda item: int(item.get("version", 0)))
        return versions

    def save_business_vision_version(self, version: dict[str, Any]) -> None:
        self._write(self.business_visions_dir / f"{version['businessId']}__{int(version['version']):04d}.json", version)

    def list_business_vision_versions(self, business_id: str) -> list[dict[str, Any]]:
        versions = [self._read(path) for path in sorted(self.business_visions_dir.glob(f"{business_id}__*.json"))]
        versions.sort(key=lambda item: int(item.get("version", 0)))
        return versions

    def get_active_business_vision(self, business_id: str) -> dict[str, Any] | None:
        versions = self.list_business_vision_versions(business_id)
        active_versions = [version for version in versions if version.get("status") == "ACTIVE"]
        return active_versions[-1] if active_versions else versions[-1] if versions else None

    def save_business_goal(self, goal: dict[str, Any]) -> None:
        self._write(self.business_goals_dir / f"{goal['businessId']}__{goal['id']}.json", goal)

    def list_business_goals(self, business_id: str, include_archived: bool = False) -> list[dict[str, Any]]:
        goals = [self._read(path) for path in sorted(self.business_goals_dir.glob(f"{business_id}__*.json"))]
        if not include_archived:
            goals = [goal for goal in goals if goal.get("status") != "ARCHIVED"]
        goals.sort(key=lambda item: str(item.get("createdAt", "")))
        return goals

    def get_business_goal(self, business_id: str, goal_id: str) -> dict[str, Any]:
        return self._read(self.business_goals_dir / f"{business_id}__{goal_id}.json")

    def save_business_constraint_version(self, constraint: dict[str, Any]) -> None:
        self._write(self.business_constraints_dir / f"{constraint['businessId']}__{constraint['id']}__{int(constraint['version']):04d}.json", constraint)

    def list_business_constraints(self, business_id: str, include_archived: bool = False) -> list[dict[str, Any]]:
        versions = [self._read(path) for path in sorted(self.business_constraints_dir.glob(f"{business_id}__*.json"))]
        latest_by_id: dict[str, dict[str, Any]] = {}
        for version in versions:
            constraint_id = str(version.get("id", ""))
            if not constraint_id:
                continue
            if int(version.get("version", 0)) >= int(latest_by_id.get(constraint_id, {}).get("version", 0)):
                latest_by_id[constraint_id] = version
        constraints = list(latest_by_id.values())
        if not include_archived:
            constraints = [constraint for constraint in constraints if constraint.get("status") != "ARCHIVED"]
        constraints.sort(key=lambda item: str(item.get("createdAt", "")))
        return constraints

    def list_business_constraint_versions(self, business_id: str, constraint_id: str) -> list[dict[str, Any]]:
        versions = [self._read(path) for path in sorted(self.business_constraints_dir.glob(f"{business_id}__{constraint_id}__*.json"))]
        versions.sort(key=lambda item: int(item.get("version", 0)))
        return versions

    def save_business_budget(self, budget: dict[str, Any]) -> None:
        self._write(self.business_budgets_dir / f"{budget['businessId']}.json", budget)

    def get_business_budget(self, business_id: str) -> dict[str, Any]:
        return self._read(self.business_budgets_dir / f"{business_id}.json")

    def save_business_success_metric(self, metric: dict[str, Any]) -> None:
        self._write(self.business_success_metrics_dir / f"{metric['businessId']}__{metric['id']}.json", metric)

    def list_business_success_metrics(self, business_id: str) -> list[dict[str, Any]]:
        metrics = [self._read(path) for path in sorted(self.business_success_metrics_dir.glob(f"{business_id}__*.json"))]
        metrics.sort(key=lambda item: str(item.get("createdAt", "")))
        return metrics

    def save_business_approval_policy(self, policy: dict[str, Any]) -> None:
        self._write(self.business_approval_policies_dir / f"{policy['businessId']}.json", policy)

    def get_business_approval_policy(self, business_id: str) -> dict[str, Any]:
        return self._read(self.business_approval_policies_dir / f"{business_id}.json")

    def save_project(self, project: dict[str, Any]) -> None:
        self._write(self.projects_dir / f"{project['id']}.json", project)

    def get_project(self, project_id: str) -> dict[str, Any]:
        return self._read(self.projects_dir / f"{project_id}.json")

    def list_projects(self, business_id: str | None = None) -> list[dict[str, Any]]:
        projects = [self._read(path) for path in sorted(self.projects_dir.glob("*.json"))]
        if business_id is not None:
            projects = [project for project in projects if project.get("businessId") == business_id]
        projects.sort(key=lambda item: str(item.get("createdAt", "")))
        return projects

    def save_workflow(self, workflow: dict[str, Any]) -> None:
        self._write(self.workflows_dir / f"{workflow['id']}.json", workflow)

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._read(self.workflows_dir / f"{workflow_id}.json")

    def list_workflows(self, status: str | None = None) -> list[dict[str, Any]]:
        workflows = [self._read(path) for path in sorted(self.workflows_dir.glob("*.json"))]
        if status is None:
            return workflows
        return [workflow for workflow in workflows if workflow.get("status") == status]

    def save_employee_output(self, output: dict[str, Any]) -> None:
        filename = f"{output['workflowId']}__{output['employeeId']}.json"
        self._write(self.employee_outputs_dir / filename, output)

    def list_employee_outputs(self, workflow_id: str) -> list[dict[str, Any]]:
        return [self._read(path) for path in sorted(self.employee_outputs_dir.glob(f"{workflow_id}__*.json"))]

    def save_report(self, report: dict[str, Any]) -> None:
        self._write(self.reports_dir / f"{report['projectId']}.json", report)

    def get_report(self, project_id: str) -> dict[str, Any]:
        return self._read(self.reports_dir / f"{project_id}.json")

    def save_approval(self, approval: dict[str, Any]) -> None:
        self._write(self.approvals_dir / f"{approval['id']}.json", approval)

    def get_approval(self, approval_id: str) -> dict[str, Any]:
        return self._read(self.approvals_dir / f"{approval_id}.json")

    def list_approvals(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        approvals = [self._read(path) for path in sorted(self.approvals_dir.glob("*.json"))]
        if project_id is not None:
            approvals = [approval for approval in approvals if approval.get("projectId") == project_id]
        if workflow_id is not None:
            approvals = [approval for approval in approvals if approval.get("workflowId") == workflow_id]
        return approvals

    def save_metric(self, metric: dict[str, Any]) -> None:
        self._write(self.metrics_dir / f"{metric['id']}.json", metric)

    def list_metrics(self, limit: int | None = None) -> list[dict[str, Any]]:
        metrics = [self._read(path) for path in sorted(self.metrics_dir.glob("*.json"))]
        metrics.sort(key=lambda item: str(item.get("createdAt", "")))
        if limit is None:
            return metrics
        return metrics[-limit:]

    def save_task(self, task: dict[str, Any]) -> None:
        self._write(self.tasks_dir / f"{task['id']}.json", task)

    def list_tasks(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        tasks = [self._read(path) for path in sorted(self.tasks_dir.glob("*.json"))]
        if project_id is not None:
            tasks = [task for task in tasks if task.get("projectId") == project_id]
        if workflow_id is not None:
            tasks = [task for task in tasks if task.get("workflowId") == workflow_id]
        return tasks

    def save_deliverable(self, deliverable: dict[str, Any]) -> None:
        self._write(self.deliverables_dir / f"{deliverable['id']}.json", deliverable)

    def list_deliverables(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        deliverables = [self._read(path) for path in sorted(self.deliverables_dir.glob("*.json"))]
        if project_id is not None:
            deliverables = [deliverable for deliverable in deliverables if deliverable.get("projectId") == project_id]
        if workflow_id is not None:
            deliverables = [deliverable for deliverable in deliverables if deliverable.get("workflowId") == workflow_id]
        return deliverables

    def save_audit_log(self, audit_log: dict[str, Any]) -> None:
        self._write(self.audit_logs_dir / f"{audit_log['id']}.json", audit_log)

    def list_audit_logs(self, project_id: str | None = None, workflow_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        audit_logs = [self._read(path) for path in sorted(self.audit_logs_dir.glob("*.json"))]
        if project_id is not None:
            audit_logs = [audit_log for audit_log in audit_logs if audit_log.get("projectId") == project_id]
        if workflow_id is not None:
            audit_logs = [audit_log for audit_log in audit_logs if audit_log.get("workflowId") == workflow_id]
        audit_logs.sort(key=lambda item: str(item.get("createdAt", "")))
        if limit is None:
            return audit_logs
        return audit_logs[-limit:]

    def save_execution_event(self, event: dict[str, Any]) -> None:
        self._write(self.execution_history_dir / f"{event['id']}.json", event)

    def list_execution_history(self, project_id: str | None = None, workflow_id: str | None = None) -> list[dict[str, Any]]:
        events = [self._read(path) for path in sorted(self.execution_history_dir.glob("*.json"))]
        if project_id is not None:
            events = [event for event in events if event.get("projectId") == project_id]
        if workflow_id is not None:
            events = [event for event in events if event.get("workflowId") == workflow_id]
        events.sort(key=lambda item: str(item.get("createdAt", "")))
        return events

    def save_product_definition(self, product_definition: dict[str, Any]) -> None:
        self._write(self.product_definitions_dir / f"{product_definition['projectId']}.json", product_definition)

    def get_product_definition(self, project_id: str) -> dict[str, Any]:
        return self._read(self.product_definitions_dir / f"{project_id}.json")

    def save_product_blueprint(self, product_blueprint: dict[str, Any]) -> None:
        self._write(self.product_blueprints_dir / f"{product_blueprint['productId']}.json", product_blueprint)

    def get_product_blueprint(self, product_id: str) -> dict[str, Any]:
        return self._read(self.product_blueprints_dir / f"{product_id}.json")

    def save_bom_report(self, product_id: str, report: dict[str, Any]) -> None:
        self._write(self.bom_reports_dir / f"{product_id}.json", report)

    def get_bom_report(self, product_id: str) -> dict[str, Any]:
        return self._read(self.bom_reports_dir / f"{product_id}.json")

    def save_cost_report(self, product_id: str, report: dict[str, Any]) -> None:
        self._write(self.cost_reports_dir / f"{product_id}.json", report)

    def get_cost_report(self, product_id: str) -> dict[str, Any]:
        return self._read(self.cost_reports_dir / f"{product_id}.json")

    def save_supplier_report(self, product_id: str, report: dict[str, Any]) -> None:
        self._write(self.supplier_reports_dir / f"{product_id}.json", report)

    def get_supplier_report(self, product_id: str) -> dict[str, Any]:
        return self._read(self.supplier_reports_dir / f"{product_id}.json")

    def save_packaging_report(self, product_id: str, report: dict[str, Any]) -> None:
        self._write(self.packaging_reports_dir / f"{product_id}.json", report)

    def get_packaging_report(self, product_id: str) -> dict[str, Any]:
        return self._read(self.packaging_reports_dir / f"{product_id}.json")

    def save_profitability_report(self, product_id: str, report: dict[str, Any]) -> None:
        self._write(self.profitability_reports_dir / f"{product_id}.json", report)

    def get_profitability_report(self, product_id: str) -> dict[str, Any]:
        return self._read(self.profitability_reports_dir / f"{product_id}.json")

    def save_manufacturing_plan(self, product_id: str, report: dict[str, Any]) -> None:
        self._write(self.manufacturing_plans_dir / f"{product_id}.json", report)

    def get_manufacturing_plan(self, product_id: str) -> dict[str, Any]:
        return self._read(self.manufacturing_plans_dir / f"{product_id}.json")

    def save_creative_pack(self, creative_pack: dict[str, Any]) -> None:
        self._write(self.creative_packs_dir / f"{creative_pack['creativeId']}.json", creative_pack)

    def get_creative_pack(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.creative_packs_dir / f"{creative_id}.json")

    def creative_asset_dir(self, creative_id: str) -> Path:
        path = self.creative_assets_dir / creative_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_brand_report(self, creative_id: str, report: dict[str, Any]) -> None:
        self._write(self.brand_reports_dir / f"{creative_id}.json", report)

    def get_brand_report(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.brand_reports_dir / f"{creative_id}.json")

    def save_logo_report(self, creative_id: str, report: dict[str, Any]) -> None:
        self._write(self.logo_reports_dir / f"{creative_id}.json", report)

    def get_logo_report(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.logo_reports_dir / f"{creative_id}.json")

    def save_creative_packaging_report(self, creative_id: str, report: dict[str, Any]) -> None:
        self._write(self.creative_packaging_reports_dir / f"{creative_id}.json", report)

    def get_creative_packaging_report(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.creative_packaging_reports_dir / f"{creative_id}.json")

    def save_mockup_report(self, creative_id: str, report: dict[str, Any]) -> None:
        self._write(self.mockup_reports_dir / f"{creative_id}.json", report)

    def get_mockup_report(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.mockup_reports_dir / f"{creative_id}.json")

    def save_marketplace_creative_report(self, creative_id: str, report: dict[str, Any]) -> None:
        self._write(self.marketplace_creative_reports_dir / f"{creative_id}.json", report)

    def get_marketplace_creative_report(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.marketplace_creative_reports_dir / f"{creative_id}.json")

    def save_social_creative_report(self, creative_id: str, report: dict[str, Any]) -> None:
        self._write(self.social_creative_reports_dir / f"{creative_id}.json", report)

    def get_social_creative_report(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.social_creative_reports_dir / f"{creative_id}.json")

    def save_copy_report(self, creative_id: str, report: dict[str, Any]) -> None:
        self._write(self.copy_reports_dir / f"{creative_id}.json", report)

    def get_copy_report(self, creative_id: str) -> dict[str, Any]:
        return self._read(self.copy_reports_dir / f"{creative_id}.json")

    def save_marketing_pack(self, marketing_pack: dict[str, Any]) -> None:
        self._write(self.marketing_packs_dir / f"{marketing_pack['marketingId']}.json", marketing_pack)

    def get_marketing_pack(self, marketing_id: str) -> dict[str, Any]:
        return self._read(self.marketing_packs_dir / f"{marketing_id}.json")

    def save_marketing_strategy_report(self, marketing_id: str, report: dict[str, Any]) -> None:
        self._write(self.marketing_strategy_reports_dir / f"{marketing_id}.json", report)

    def get_marketing_strategy_report(self, marketing_id: str) -> dict[str, Any]:
        return self._read(self.marketing_strategy_reports_dir / f"{marketing_id}.json")

    def save_seo_report(self, marketing_id: str, report: dict[str, Any]) -> None:
        self._write(self.seo_reports_dir / f"{marketing_id}.json", report)

    def get_seo_report(self, marketing_id: str) -> dict[str, Any]:
        return self._read(self.seo_reports_dir / f"{marketing_id}.json")

    def save_social_marketing_report(self, marketing_id: str, report: dict[str, Any]) -> None:
        self._write(self.social_marketing_reports_dir / f"{marketing_id}.json", report)

    def get_social_marketing_report(self, marketing_id: str) -> dict[str, Any]:
        return self._read(self.social_marketing_reports_dir / f"{marketing_id}.json")

    def save_ads_report(self, marketing_id: str, report: dict[str, Any]) -> None:
        self._write(self.ads_reports_dir / f"{marketing_id}.json", report)

    def get_ads_report(self, marketing_id: str) -> dict[str, Any]:
        return self._read(self.ads_reports_dir / f"{marketing_id}.json")

    def save_listing_report(self, marketing_id: str, report: dict[str, Any]) -> None:
        self._write(self.listing_reports_dir / f"{marketing_id}.json", report)

    def get_listing_report(self, marketing_id: str) -> dict[str, Any]:
        return self._read(self.listing_reports_dir / f"{marketing_id}.json")

    def save_launch_report(self, marketing_id: str, report: dict[str, Any]) -> None:
        self._write(self.launch_reports_dir / f"{marketing_id}.json", report)

    def get_launch_report(self, marketing_id: str) -> dict[str, Any]:
        return self._read(self.launch_reports_dir / f"{marketing_id}.json")

    def save_business_launch_package(self, launch_package: dict[str, Any]) -> None:
        self._write(self.business_launch_packages_dir / f"{launch_package['launchId']}.json", launch_package)

    def get_business_launch_package(self, launch_id: str) -> dict[str, Any]:
        return self._read(self.business_launch_packages_dir / f"{launch_id}.json")

    def save_launch_checklist(self, launch_id: str, checklist: dict[str, Any] | list[dict[str, Any]]) -> None:
        self._write(self.business_launch_checklists_dir / f"{launch_id}.json", {"launchId": launch_id, "checklist": checklist})

    def get_launch_checklist(self, launch_id: str) -> dict[str, Any]:
        return self._read(self.business_launch_checklists_dir / f"{launch_id}.json")

    def save_publishing_plan(self, launch_id: str, plan: dict[str, Any]) -> None:
        self._write(self.publishing_plans_dir / f"{launch_id}.json", plan)

    def get_publishing_plan(self, launch_id: str) -> dict[str, Any]:
        return self._read(self.publishing_plans_dir / f"{launch_id}.json")

    def save_asset_manifest(self, launch_id: str, manifest: dict[str, Any]) -> None:
        self._write(self.asset_manifests_dir / f"{launch_id}.json", manifest)

    def get_asset_manifest(self, launch_id: str) -> dict[str, Any]:
        return self._read(self.asset_manifests_dir / f"{launch_id}.json")

    def save_business_launch_report(self, launch_id: str, report: dict[str, Any]) -> None:
        self._write(self.business_launch_reports_dir / f"{launch_id}.json", report)

    def get_business_launch_report(self, launch_id: str) -> dict[str, Any]:
        return self._read(self.business_launch_reports_dir / f"{launch_id}.json")

    def save_business_operating_plan(self, plan: dict[str, Any]) -> None:
        self._write(self.business_operating_plans_dir / f"{plan['businessId']}.json", plan)

    def get_business_operating_plan(self, business_id: str) -> dict[str, Any]:
        return self._read(self.business_operating_plans_dir / f"{business_id}.json")

    def save_digital_twin(self, business_id: str, digital_twin: dict[str, Any]) -> None:
        self._write(self.digital_twins_dir / f"{business_id}.json", digital_twin)

    def get_digital_twin(self, business_id: str) -> dict[str, Any]:
        return self._read(self.digital_twins_dir / f"{business_id}.json")

    def save_knowledge_graph(self, business_id: str, knowledge_graph: dict[str, Any]) -> None:
        self._write(self.knowledge_graphs_dir / f"{business_id}.json", knowledge_graph)

    def get_knowledge_graph(self, business_id: str) -> dict[str, Any]:
        return self._read(self.knowledge_graphs_dir / f"{business_id}.json")

    def save_decision_register(self, business_id: str, decision_register: dict[str, Any]) -> None:
        self._write(self.decision_registers_dir / f"{business_id}.json", decision_register)

    def get_decision_register(self, business_id: str) -> dict[str, Any]:
        return self._read(self.decision_registers_dir / f"{business_id}.json")

    def save_simulation_report(self, business_id: str, simulation_report: dict[str, Any]) -> None:
        self._write(self.simulation_reports_dir / f"{business_id}.json", simulation_report)

    def get_simulation_report(self, business_id: str) -> dict[str, Any]:
        return self._read(self.simulation_reports_dir / f"{business_id}.json")

    def save_business_health_report(self, business_id: str, health_report: dict[str, Any]) -> None:
        self._write(self.business_health_reports_dir / f"{business_id}.json", health_report)

    def get_business_health_report(self, business_id: str) -> dict[str, Any]:
        return self._read(self.business_health_reports_dir / f"{business_id}.json")

    def save_recommendation_report(self, business_id: str, recommendation_report: dict[str, Any]) -> None:
        self._write(self.recommendation_reports_dir / f"{business_id}.json", recommendation_report)

    def get_recommendation_report(self, business_id: str) -> dict[str, Any]:
        return self._read(self.recommendation_reports_dir / f"{business_id}.json")

    def save_business_metric_event(self, event: dict[str, Any]) -> None:
        self._write(self.business_metric_events_dir / f"{event['businessId']}__{event['id']}.json", event)

    def list_business_metric_events(self, business_id: str) -> list[dict[str, Any]]:
        events = [self._read(path) for path in sorted(self.business_metric_events_dir.glob(f"{business_id}__*.json"))]
        events.sort(key=lambda item: str(item.get("observedAt", item.get("createdAt", ""))))
        return events

    def save_business_dashboard(self, business_id: str, dashboard: dict[str, Any]) -> None:
        self._write(self.business_dashboards_dir / f"{business_id}.json", dashboard)

    def get_business_dashboard(self, business_id: str) -> dict[str, Any]:
        return self._read(self.business_dashboards_dir / f"{business_id}.json")

    def save_business_alerts(self, business_id: str, alerts: dict[str, Any]) -> None:
        self._write(self.business_alerts_dir / f"{business_id}.json", alerts)

    def get_business_alerts(self, business_id: str) -> dict[str, Any]:
        return self._read(self.business_alerts_dir / f"{business_id}.json")

    def save_business_knowledge_entry(self, entry: dict[str, Any]) -> None:
        self._write(self.business_knowledge_dir / f"{entry['businessId']}__{entry['id']}.json", entry)

    def list_business_knowledge(self, business_id: str) -> list[dict[str, Any]]:
        entries = [self._read(path) for path in sorted(self.business_knowledge_dir.glob(f"{business_id}__*.json"))]
        entries.sort(key=lambda item: str(item.get("createdAt", "")))
        return entries

    def save_product_knowledge(self, entry: dict[str, Any]) -> None:
        project_id = entry["projectId"]
        existing = self.list_product_knowledge(project_id=project_id)
        sequence = len(existing) + 1
        self._write(self.product_knowledge_dir / f"{project_id}__{sequence:03d}.json", entry)

    def list_product_knowledge(self, project_id: str | None = None) -> list[dict[str, Any]]:
        entries = [self._read(path) for path in sorted(self.product_knowledge_dir.glob("*.json"))]
        if project_id is not None:
            entries = [entry for entry in entries if entry.get("projectId") == project_id]
        return entries

    def _write(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _read(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Genesis store record not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

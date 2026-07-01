"""Minimal Genesis AI API runtime with BusinessOS sprint endpoints."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from apps.dashboard import render_business_dashboard
from apps.errors import GenesisError, bad_request, not_found
from apps.founder import FounderBusinessRuntime
from apps.integrations.registry import integration_status
from apps.observability import summarize_metrics
from apps.orchestrator import GenesisOrchestrator
from apps.project import ProjectLifecycleRuntime
from apps.security import ApiPrincipal, authenticate_request
from apps.storage import JsonStore
from apps.workflow import WorkflowEngine
from config import RuntimeConfig, configure_logging, load_runtime_config

API_VERSION = "1.0.0-foundation"


class GenesisApiHandler(BaseHTTPRequestHandler):
    """HTTP handler for runtime bootstrap, research, and product endpoints."""

    server_version = "GenesisAI/0.3"

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code: int, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            raise bad_request("Request body is required")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise bad_request("Request body must be valid JSON") from exc

    def _read_optional_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise bad_request("Request body must be valid JSON") from exc

    @property
    def store(self) -> JsonStore:
        return self.server.store  # type: ignore[attr-defined]

    def _authorize(self, roles: set[str]) -> ApiPrincipal:
        config: RuntimeConfig = self.server.runtime_config  # type: ignore[attr-defined]
        principal = authenticate_request(self.headers, config, roles)
        self.server.current_principal = principal  # type: ignore[attr-defined]
        return principal

    def _founder_id(self) -> str:
        return self.headers.get("X-Genesis-Founder-ID", "founder").strip() or "founder"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        config: RuntimeConfig = self.server.runtime_config  # type: ignore[attr-defined]
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/health":
                self._send_json(200, config.health_payload("api"))
                return
            if parsed.path == "/version":
                self._send_json(200, {"app": config.app_name, "version": API_VERSION, "release": "Sprint 8 - Genesis BusinessOS Foundation"})
                return
            self._authorize({"founder", "operator", "viewer"})
            if parsed.path == "/integrations/status":
                self._send_json(200, integration_status())
                return
            if parsed.path == "/founder/profile":
                try:
                    self._send_json(200, FounderBusinessRuntime(self.store).get_founder_profile(founder_id=self._founder_id()))
                except FileNotFoundError as exc:
                    raise not_found("Founder profile not found") from exc
                return
            if parsed.path == "/businesses":
                self._send_json(200, FounderBusinessRuntime(self.store).list_businesses(founder_id=self._founder_id()))
                return
            if parsed.path.startswith("/businesses/"):
                business_path = parsed.path.removeprefix("/businesses/").strip("/")
                parts = [part for part in business_path.split("/") if part]
                if not parts:
                    raise bad_request("Business ID is required")
                business_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                runtime = FounderBusinessRuntime(self.store)
                try:
                    if section is None or section == "dashboard":
                        self._send_json(200, runtime.business_dashboard(business_id))
                    elif section == "vision":
                        self._send_json(200, {"businessId": business_id, "activeVision": self.store.get_active_business_vision(business_id), "versions": self.store.list_business_vision_versions(business_id)})
                    elif section == "goals":
                        self._send_json(200, {"businessId": business_id, "goals": self.store.list_business_goals(business_id, include_archived=True)})
                    elif section == "constraints":
                        self._send_json(200, {"businessId": business_id, "constraints": self.store.list_business_constraints(business_id, include_archived=True)})
                    elif section == "budget":
                        self._send_json(200, self.store.get_business_budget(business_id))
                    elif section == "success-metrics":
                        self._send_json(200, {"businessId": business_id, "metrics": self.store.list_business_success_metrics(business_id)})
                    elif section == "approval-policy":
                        self._send_json(200, self.store.get_business_approval_policy(business_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Business resource not found: {business_id}") from exc
            if parsed.path == "/metrics":
                metrics = self.store.list_metrics()
                self._send_json(200, {"summary": summarize_metrics(metrics), "metrics": metrics})
                return
            if parsed.path.startswith("/dashboard/businessos/"):
                business_id = parsed.path.removeprefix("/dashboard/businessos/").strip("/")
                if not business_id:
                    raise bad_request("Business ID is required")
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    dashboard = orchestrator.get_business_dashboard(business_id)
                    alerts = orchestrator.get_business_alerts(business_id)
                    knowledge = orchestrator.get_business_knowledge(business_id)
                    self._send_html(200, render_business_dashboard(dashboard, alerts, knowledge))
                except FileNotFoundError as exc:
                    raise not_found(f"Business dashboard not found: {business_id}") from exc
                return
            if parsed.path.startswith("/brand/"):
                creative_id = parsed.path.removeprefix("/brand/").strip("/")
                if not creative_id:
                    raise bad_request("Creative ID is required")
                try:
                    self._send_json(200, GenesisOrchestrator(self.store).get_creative_brand(creative_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Brand identity not found: {creative_id}") from exc
                return
            if parsed.path.startswith("/packaging/"):
                creative_id = parsed.path.removeprefix("/packaging/").strip("/")
                if not creative_id:
                    raise bad_request("Creative ID is required")
                try:
                    self._send_json(200, GenesisOrchestrator(self.store).get_creative_packaging(creative_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Packaging brief not found: {creative_id}") from exc
                return
            if parsed.path.startswith("/campaigns/"):
                marketing_id = parsed.path.removeprefix("/campaigns/").strip("/")
                if not marketing_id:
                    raise bad_request("Marketing ID is required")
                try:
                    marketing = GenesisOrchestrator(self.store).get_marketing(marketing_id)
                    self._send_json(200, {"advertisingPlan": marketing["ads"], "launchPlan": marketing["launch"], "aiDeliverables": marketing["marketingPack"].get("aiDeliverables", {})})
                except FileNotFoundError as exc:
                    raise not_found(f"Campaigns not found: {marketing_id}") from exc
                return
            if parsed.path.startswith("/content-calendar/"):
                marketing_id = parsed.path.removeprefix("/content-calendar/").strip("/")
                if not marketing_id:
                    raise bad_request("Marketing ID is required")
                try:
                    self._send_json(200, GenesisOrchestrator(self.store).get_marketing_social(marketing_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Content calendar not found: {marketing_id}") from exc
                return
            if parsed.path.startswith("/marketing/"):
                marketing_path = parsed.path.removeprefix("/marketing/").strip("/")
                parts = [part for part in marketing_path.split("/") if part]
                if not parts:
                    raise bad_request("Marketing ID is required")
                marketing_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if section is None:
                        self._send_json(200, orchestrator.get_marketing(marketing_id))
                    elif section == "pack":
                        self._send_json(200, orchestrator.get_marketing_pack(marketing_id))
                    elif section == "strategy":
                        self._send_json(200, orchestrator.get_marketing_strategy(marketing_id))
                    elif section == "seo":
                        self._send_json(200, orchestrator.get_marketing_seo(marketing_id))
                    elif section == "social":
                        self._send_json(200, orchestrator.get_marketing_social(marketing_id))
                    elif section == "ads":
                        self._send_json(200, orchestrator.get_marketing_ads(marketing_id))
                    elif section == "listing":
                        self._send_json(200, orchestrator.get_marketing_listing(marketing_id))
                    elif section == "launch":
                        self._send_json(200, orchestrator.get_marketing_launch(marketing_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Marketing pack not found: {marketing_id}") from exc
            if parsed.path.startswith("/sales/"):
                sales_path = parsed.path.removeprefix("/sales/").strip("/")
                parts = [part for part in sales_path.split("/") if part]
                if not parts:
                    raise bad_request("Sales ID is required")
                sales_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if section is None:
                        self._send_json(200, orchestrator.get_sales(sales_id))
                    elif section == "package":
                        self._send_json(200, orchestrator.get_sales_package(sales_id))
                    elif section == "crm":
                        self._send_json(200, orchestrator.get_sales_crm(sales_id))
                    elif section == "quotations":
                        self._send_json(200, orchestrator.get_sales_quotations(sales_id))
                    elif section == "pipeline":
                        self._send_json(200, orchestrator.get_sales_pipeline(sales_id))
                    elif section == "orders":
                        self._send_json(200, orchestrator.get_sales_orders(sales_id))
                    elif section == "analytics":
                        self._send_json(200, orchestrator.get_sales_analytics(sales_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Sales package not found: {sales_id}") from exc
            if parsed.path.startswith("/launch/"):
                launch_path = parsed.path.removeprefix("/launch/").strip("/")
                parts = [part for part in launch_path.split("/") if part]
                if not parts:
                    raise bad_request("Launch ID is required")
                launch_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if section is None:
                        self._send_json(200, orchestrator.get_business_launch(launch_id))
                    elif section == "package":
                        self._send_json(200, orchestrator.get_business_launch_package(launch_id))
                    elif section == "status":
                        self._send_json(200, orchestrator.get_business_launch_status(launch_id))
                    elif section == "assets":
                        self._send_json(200, orchestrator.get_business_launch_assets(launch_id))
                    elif section == "report":
                        self._send_json(200, orchestrator.get_business_launch_report(launch_id))
                    elif section == "checklist":
                        self._send_json(200, orchestrator.get_business_launch_checklist(launch_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Business launch package not found: {launch_id}") from exc
            if parsed.path.startswith("/business-intelligence/"):
                intelligence_path = parsed.path.removeprefix("/business-intelligence/").strip("/")
                parts = [part for part in intelligence_path.split("/") if part]
                if not parts:
                    raise bad_request("Business ID is required")
                business_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if section is None or section == "report":
                        self._send_json(200, orchestrator.get_business_intelligence_report(business_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Business intelligence report not found: {business_id}") from exc
            if parsed.path.startswith("/businessos/"):
                business_path = parsed.path.removeprefix("/businessos/").strip("/")
                parts = [part for part in business_path.split("/") if part]
                if not parts:
                    raise bad_request("Business ID is required")
                business_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if section is None:
                        self._send_json(200, orchestrator.get_businessos(business_id))
                    elif section == "plan":
                        self._send_json(200, orchestrator.get_business_operating_plan(business_id))
                    elif section == "digital-twin":
                        self._send_json(200, orchestrator.get_digital_twin(business_id))
                    elif section == "knowledge-graph":
                        self._send_json(200, orchestrator.get_knowledge_graph(business_id))
                    elif section == "decisions":
                        self._send_json(200, orchestrator.get_decisions(business_id))
                    elif section == "simulations":
                        self._send_json(200, orchestrator.get_simulations(business_id))
                    elif section == "health":
                        self._send_json(200, orchestrator.get_business_health(business_id))
                    elif section == "recommendations":
                        self._send_json(200, orchestrator.get_recommendations(business_id))
                    elif section == "dashboard":
                        self._send_json(200, orchestrator.get_business_dashboard(business_id))
                    elif section == "alerts":
                        self._send_json(200, orchestrator.get_business_alerts(business_id))
                    elif section == "knowledge":
                        self._send_json(200, orchestrator.get_business_knowledge(business_id))
                    elif section == "metrics":
                        self._send_json(200, orchestrator.list_business_metric_events(business_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"BusinessOS plan not found: {business_id}") from exc
            if parsed.path.startswith("/v2/"):
                v2_path = parsed.path.removeprefix("/v2/").strip("/")
                parts = [part for part in v2_path.split("/") if part]
                if len(parts) < 2:
                    raise bad_request("V2 route must include resource and business ID")
                resource, business_id = parts[0], parts[1]
                section = parts[2] if len(parts) > 2 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if resource == "organizational-intelligence" and section in {None, "report"}:
                        self._send_json(200, orchestrator.get_organizational_intelligence_report(business_id))
                    elif resource == "organizational-intelligence" and section == "knowledge-base":
                        self._send_json(200, orchestrator.get_executive_knowledge_base(business_id))
                    elif resource == "simulation" and section in {None, "report"}:
                        self._send_json(200, orchestrator.get_v2_simulation_report(business_id))
                    elif resource == "simulation" and section == "decisions":
                        self._send_json(200, orchestrator.get_v2_decision_register(business_id))
                    elif resource == "executive-planning" and section in {None, "report"}:
                        self._send_json(200, orchestrator.get_executive_planning_report(business_id))
                    elif resource == "opportunity-discovery" and section in {None, "report"}:
                        self._send_json(200, orchestrator.get_opportunity_discovery_report(business_id))
                    elif resource == "optimization" and section in {None, "report"}:
                        self._send_json(200, orchestrator.get_execution_optimization_report(business_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"V2 report not found: {business_id}") from exc
            if parsed.path.startswith("/enterprise/integration-platforms/"):
                platform_id = parsed.path.removeprefix("/enterprise/integration-platforms/").strip("/")
                if not platform_id:
                    raise bad_request("Platform ID is required")
                try:
                    self._send_json(200, GenesisOrchestrator(self.store).get_enterprise_integration_platform(platform_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Enterprise integration platform not found: {platform_id}") from exc
                return
            platform_getters = {
                "/platform/ai-agent-platforms/": GenesisOrchestrator(self.store).get_ai_agent_platform,
                "/platform/digital-enterprises/": GenesisOrchestrator(self.store).get_digital_enterprise,
                "/platform/autonomous-enterprises/": GenesisOrchestrator(self.store).get_autonomous_enterprise,
                "/platform/ecosystems/": GenesisOrchestrator(self.store).get_platform_ecosystem,
                "/platform/collective-intelligence/": GenesisOrchestrator(self.store).get_collective_intelligence_platform,
            }
            for prefix, getter in platform_getters.items():
                if parsed.path.startswith(prefix):
                    platform_id = parsed.path.removeprefix(prefix).strip("/")
                    if not platform_id:
                        raise bad_request("Platform ID is required")
                    try:
                        self._send_json(200, getter(platform_id))
                    except FileNotFoundError as exc:
                        raise not_found(f"Platform package not found: {platform_id}") from exc
                    return
            if parsed.path.startswith("/enterprise/"):
                organization_id = parsed.path.removeprefix("/enterprise/").strip("/")
                if not organization_id:
                    raise bad_request("Organization ID is required")
                try:
                    self._send_json(200, GenesisOrchestrator(self.store).get_enterprise_organization(organization_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Enterprise organization not found: {organization_id}") from exc
                return
            if parsed.path.startswith("/creative/"):
                creative_path = parsed.path.removeprefix("/creative/").strip("/")
                parts = [part for part in creative_path.split("/") if part]
                if not parts:
                    raise bad_request("Creative ID is required")
                creative_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if section is None:
                        self._send_json(200, orchestrator.get_creative(creative_id))
                    elif section == "pack":
                        self._send_json(200, orchestrator.get_creative_pack(creative_id))
                    elif section == "brand":
                        self._send_json(200, orchestrator.get_creative_brand(creative_id))
                    elif section == "logo":
                        self._send_json(200, orchestrator.get_creative_logo(creative_id))
                    elif section == "packaging":
                        self._send_json(200, orchestrator.get_creative_packaging(creative_id))
                    elif section == "mockups":
                        self._send_json(200, orchestrator.get_creative_mockups(creative_id))
                    elif section == "marketplace":
                        self._send_json(200, orchestrator.get_creative_marketplace(creative_id))
                    elif section == "social":
                        self._send_json(200, orchestrator.get_creative_social(creative_id))
                    elif section == "copy":
                        self._send_json(200, orchestrator.get_creative_copy(creative_id))
                    elif section == "assets":
                        self._send_json(200, orchestrator.get_creative_assets(creative_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Creative pack not found: {creative_id}") from exc
            if parsed.path.startswith("/products/"):
                product_path = parsed.path.removeprefix("/products/").strip("/")
                parts = [part for part in product_path.split("/") if part]
                if not parts:
                    raise bad_request("Product ID is required")
                product_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                orchestrator = GenesisOrchestrator(self.store)
                try:
                    if section is None:
                        self._send_json(200, orchestrator.get_product(product_id))
                    elif section == "blueprint":
                        self._send_json(200, orchestrator.get_product_blueprint(product_id))
                    elif section == "bom":
                        self._send_json(200, orchestrator.get_product_bom(product_id))
                    elif section == "cost":
                        self._send_json(200, orchestrator.get_product_cost(product_id))
                    elif section == "suppliers":
                        self._send_json(200, orchestrator.get_product_suppliers(product_id))
                    elif section == "packaging":
                        self._send_json(200, orchestrator.get_product_packaging(product_id))
                    elif section == "profitability":
                        self._send_json(200, orchestrator.get_product_profitability(product_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Product not found: {product_id}") from exc
            if parsed.path.startswith("/workflows/"):
                workflow_path = parsed.path.removeprefix("/workflows/").strip("/")
                parts = [part for part in workflow_path.split("/") if part]
                if not parts:
                    raise bad_request("Workflow ID is required")
                workflow_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                engine = WorkflowEngine(self.store)
                try:
                    if section is None:
                        self._send_json(200, {"workflow": self.store.get_workflow(workflow_id)})
                    elif section == "progress":
                        self._send_json(200, engine.progress(workflow_id))
                    elif section == "history":
                        self._send_json(200, engine.history(workflow_id))
                    elif section == "notifications":
                        self._send_json(200, engine.notifications(workflow_id))
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                    return
                except FileNotFoundError as exc:
                    raise not_found(f"Workflow not found: {workflow_id}") from exc
            if parsed.path.startswith("/projects/"):
                project_path = parsed.path.removeprefix("/projects/").strip("/")
                parts = [part for part in project_path.split("/") if part]
                if not parts:
                    raise bad_request("Project ID is required")
                project_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                try:
                    runtime = ProjectLifecycleRuntime(self.store)
                    if section is None:
                        self._send_json(200, GenesisOrchestrator(self.store).get_project(project_id))
                    elif section == "dashboard":
                        self._send_json(200, runtime.dashboard(project_id))
                    elif section == "timeline":
                        self._send_json(200, runtime.timeline(project_id))
                    elif section == "health":
                        self._send_json(200, runtime.health(project_id))
                    elif section == "readiness":
                        reports = self.store.list_project_readiness(project_id)
                        self._send_json(200, {"projectId": project_id, "reports": reports, "latest": reports[-1] if reports else None})
                    elif section == "audit":
                        self._send_json(200, {"projectId": project_id, "auditLogs": self.store.list_audit_logs(project_id=project_id), "export": {"format": "json"}})
                    else:
                        self._send_json(404, {"status": "not_found", "path": parsed.path})
                except FileNotFoundError as exc:
                    raise not_found(f"Project not found: {project_id}") from exc
                return
            if parsed.path.startswith("/approvals/"):
                approval_id = parsed.path.removeprefix("/approvals/").strip("/")
                if not approval_id:
                    raise bad_request("Approval ID is required")
                try:
                    self._send_json(200, self.store.get_approval(approval_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Approval not found: {approval_id}") from exc
                return
            if parsed.path.startswith("/reports/"):
                project_id = parsed.path.removeprefix("/reports/").strip("/")
                if not project_id:
                    raise bad_request("Project ID is required")
                try:
                    self._send_json(200, self.store.get_report(project_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Research report not found for project {project_id}") from exc
                return
            if parsed.path.startswith("/product-definitions/"):
                project_id = parsed.path.removeprefix("/product-definitions/").strip("/")
                if not project_id:
                    raise bad_request("Project ID is required")
                try:
                    self._send_json(200, GenesisOrchestrator(self.store).get_product_definition(project_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Product definition not found for project {project_id}") from exc
                return
            self._send_json(404, {"status": "not_found", "path": parsed.path})
        except GenesisError as exc:
            self._send_json(exc.status_code, exc.to_payload())

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/approvals/"):
                self._authorize({"founder"})
            else:
                self._authorize({"founder", "operator"})
            if parsed.path == "/founder/profile":
                result = FounderBusinessRuntime(self.store).upsert_founder_profile(self._read_json(), founder_id=self._founder_id())
                self._send_json(200, result)
                return
            if parsed.path == "/businesses":
                payload = self._read_json()
                result = FounderBusinessRuntime(self.store).create_business(payload, founder_id=self._founder_id(), idempotency_key=self.headers.get("Idempotency-Key"), draft=payload.get("draft") is True)
                self._send_json(201, result)
                return
            if parsed.path.startswith("/businesses/"):
                business_path = parsed.path.removeprefix("/businesses/").strip("/")
                parts = [part for part in business_path.split("/") if part]
                if not parts:
                    raise bad_request("Business ID is required")
                business_id = parts[0]
                section = parts[1] if len(parts) > 1 else None
                runtime = FounderBusinessRuntime(self.store)
                if len(parts) == 4 and parts[1] == "projects" and parts[3] == "start-planning":
                    self._send_json(201, runtime.start_project_planning(business_id, parts[2], founder_id=self._founder_id()))
                    return
                payload = self._read_json()
                if section == "vision":
                    content = payload.get("content")
                    if not isinstance(content, str):
                        raise bad_request("content must be a string")
                    content_format = payload.get("contentFormat", "markdown")
                    if not isinstance(content_format, str):
                        raise bad_request("contentFormat must be a string")
                    self._send_json(201, runtime.set_business_vision(business_id, content, founder_id=self._founder_id(), content_format=content_format))
                    return
                if len(parts) == 3 and parts[1] == "goals":
                    self._send_json(200, runtime.update_business_goal(business_id, parts[2], payload, founder_id=self._founder_id()))
                    return
                if section == "goals":
                    self._send_json(201, runtime.add_business_goal(business_id, payload, founder_id=self._founder_id()))
                    return
                if len(parts) == 3 and parts[1] == "constraints":
                    self._send_json(200, runtime.update_business_constraint(business_id, parts[2], payload, founder_id=self._founder_id()))
                    return
                if section == "constraints":
                    self._send_json(201, runtime.add_business_constraint(business_id, payload, founder_id=self._founder_id()))
                    return
                if section == "budget":
                    self._send_json(200, runtime.set_business_budget(business_id, payload, founder_id=self._founder_id()))
                    return
                if section == "success-metrics":
                    self._send_json(201, runtime.add_success_metric(business_id, payload, founder_id=self._founder_id()))
                    return
                if section == "approval-policy":
                    self._send_json(200, runtime.set_approval_policy(business_id, payload, founder_id=self._founder_id()))
                    return
                if section == "projects":
                    self._send_json(201, runtime.create_project(business_id, payload, founder_id=self._founder_id()))
                    return
                if len(parts) == 3 and parts[1] == "projects":
                    raise bad_request("Project action is required")
            if parsed.path == "/marketing/generate":
                payload = self._read_json()
                creative_id = payload.get("creativeId")
                if not isinstance(creative_id, str):
                    raise bad_request("creativeId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_marketing_pack(creative_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/launch/generate":
                payload = self._read_json()
                marketing_id = payload.get("marketingId")
                if not isinstance(marketing_id, str):
                    raise bad_request("marketingId must be a string")
                approval_mode = payload.get("approvalMode", "manual")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_business_launch_package(marketing_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/sales/generate":
                payload = self._read_json()
                marketing_id = payload.get("marketingId")
                if not isinstance(marketing_id, str):
                    raise bad_request("marketingId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_sales_package(marketing_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/business-intelligence/generate":
                payload = self._read_json()
                launch_id = payload.get("launchId")
                if not isinstance(launch_id, str):
                    raise bad_request("launchId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_business_intelligence_report(launch_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/businessos/generate":
                payload = self._read_json()
                launch_id = payload.get("launchId")
                if not isinstance(launch_id, str):
                    raise bad_request("launchId must be a string")
                approval_mode = payload.get("approvalMode", "manual")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_business_operating_plan(launch_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path.startswith("/businessos/") and parsed.path.endswith("/metrics"):
                business_id = parsed.path.removeprefix("/businessos/").removesuffix("/metrics").strip("/")
                if not business_id:
                    raise bad_request("Business ID is required")
                payload = self._read_json()
                metrics = payload.get("metrics")
                if not isinstance(metrics, dict):
                    raise bad_request("metrics must be an object")
                source = payload.get("source", "manual")
                if not isinstance(source, str):
                    raise bad_request("source must be a string")
                observed_at = payload.get("observedAt")
                if observed_at is not None and not isinstance(observed_at, str):
                    raise bad_request("observedAt must be a string")
                result = GenesisOrchestrator(self.store).ingest_business_metrics(business_id, metrics, source=source, observed_at=observed_at)
                self._send_json(201, result)
                return
            if parsed.path == "/v2/organizational-intelligence/generate":
                payload = self._read_json()
                business_id = payload.get("businessId")
                if not isinstance(business_id, str):
                    raise bad_request("businessId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_organizational_intelligence_report(business_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/v2/simulation/generate":
                payload = self._read_json()
                business_id = payload.get("businessId")
                if not isinstance(business_id, str):
                    raise bad_request("businessId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_simulation_report(business_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/v2/executive-planning/generate":
                payload = self._read_json()
                business_id = payload.get("businessId")
                if not isinstance(business_id, str):
                    raise bad_request("businessId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_executive_planning_report(business_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/v2/opportunity-discovery/generate":
                payload = self._read_json()
                business_id = payload.get("businessId")
                if not isinstance(business_id, str):
                    raise bad_request("businessId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_opportunity_discovery_report(business_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/v2/optimization/generate":
                payload = self._read_json()
                business_id = payload.get("businessId")
                if not isinstance(business_id, str):
                    raise bad_request("businessId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_execution_optimization_report(business_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/enterprise/organizations":
                payload = self._read_json()
                name = payload.get("name")
                if not isinstance(name, str):
                    raise bad_request("name must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                admin = payload.get("admin", "enterprise-admin")
                if not isinstance(admin, str):
                    raise bad_request("admin must be a string")
                result = GenesisOrchestrator(self.store).create_enterprise_organization(name, approval_mode=approval_mode, admin=admin)
                self._send_json(201, result)
                return
            if parsed.path == "/enterprise/integration-platforms":
                payload = self._read_json()
                name = payload.get("name", "Genesis Enterprise Integration Platform")
                if not isinstance(name, str):
                    raise bad_request("name must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                organization_id = payload.get("organizationId")
                if organization_id is not None and not isinstance(organization_id, str):
                    raise bad_request("organizationId must be a string")
                admin = payload.get("admin", "platform-admin")
                if not isinstance(admin, str):
                    raise bad_request("admin must be a string")
                result = GenesisOrchestrator(self.store).initialize_enterprise_integration_platform(name, approval_mode=approval_mode, organization_id=organization_id, admin=admin)
                self._send_json(201, result)
                return
            platform_creators = {
                "/platform/ai-agent-platforms": ("name", "Genesis AI Agent Platform", "aiAgentPlatform", GenesisOrchestrator(self.store).initialize_ai_agent_platform),
                "/platform/digital-enterprises": ("name", "Genesis Digital Enterprise", "digitalEnterprise", GenesisOrchestrator(self.store).initialize_digital_enterprise),
                "/platform/autonomous-enterprises": ("name", "Genesis Autonomous Enterprise", "autonomousEnterprise", GenesisOrchestrator(self.store).initialize_autonomous_enterprise),
                "/platform/ecosystems": ("name", "Genesis Platform Ecosystem", "platformEcosystem", GenesisOrchestrator(self.store).initialize_platform_ecosystem),
                "/platform/collective-intelligence": ("name", "Genesis Collective Enterprise Intelligence", "collectiveIntelligencePlatform", GenesisOrchestrator(self.store).initialize_collective_intelligence_platform),
            }
            if parsed.path in platform_creators:
                _, default_name, _, creator = platform_creators[parsed.path]
                payload = self._read_json()
                name = payload.get("name", default_name)
                if not isinstance(name, str):
                    raise bad_request("name must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                organization_id = payload.get("organizationId")
                if organization_id is not None and not isinstance(organization_id, str):
                    raise bad_request("organizationId must be a string")
                admin = payload.get("admin", "platform-admin")
                if not isinstance(admin, str):
                    raise bad_request("admin must be a string")
                self._send_json(201, creator(name, approval_mode=approval_mode, organization_id=organization_id, admin=admin))
                return
            if parsed.path == "/creative/generate":
                payload = self._read_json()
                product_id = payload.get("productId")
                if not isinstance(product_id, str):
                    raise bad_request("productId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_creative_pack(product_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/products/generate":
                payload = self._read_json()
                project_id = payload.get("projectId")
                if not isinstance(project_id, str):
                    raise bad_request("projectId must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).generate_product_blueprint(project_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path == "/workflows":
                payload = self._read_json()
                project_id = payload.get("projectId")
                workflow_type = payload.get("type")
                if not isinstance(project_id, str):
                    raise bad_request("projectId must be a string")
                if not isinstance(workflow_type, str):
                    raise bad_request("type must be a string")
                result = WorkflowEngine(self.store).create(
                    project_id,
                    workflow_type,
                    created_by=self._founder_id(),
                    name=payload.get("name") if isinstance(payload.get("name"), str) else None,
                    priority=payload.get("priority", "MEDIUM") if isinstance(payload.get("priority", "MEDIUM"), str) else "MEDIUM",
                    idempotency_key=self.headers.get("Idempotency-Key") or (payload.get("idempotencyKey") if isinstance(payload.get("idempotencyKey"), str) else None),
                )
                self._send_json(201, {"workflow": result})
                return
            if parsed.path == "/projects":
                payload = self._read_json()
                idea = payload.get("idea")
                if not isinstance(idea, str):
                    raise bad_request("idea must be a string")
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                constraints = payload.get("constraints", [])
                preferences = payload.get("preferences", {})
                if constraints is not None and not isinstance(constraints, list):
                    raise bad_request("constraints must be a list")
                if preferences is not None and not isinstance(preferences, dict):
                    raise bad_request("preferences must be an object")
                result = GenesisOrchestrator(self.store).submit_idea(
                    idea,
                    approval_mode=approval_mode,
                    country=payload.get("country") if isinstance(payload.get("country"), str) else None,
                    budget=payload.get("budget") if isinstance(payload.get("budget"), str) else None,
                    timeline=payload.get("timeline") if isinstance(payload.get("timeline"), str) else None,
                    constraints=constraints,
                    preferences=preferences,
                )
                self._send_json(201, result)
                return
            if parsed.path.startswith("/projects/") and not parsed.path.endswith("/product-definition"):
                project_path = parsed.path.removeprefix("/projects/").strip("/")
                parts = [part for part in project_path.split("/") if part]
                if len(parts) < 2:
                    raise bad_request("Project action is required")
                project_id = parts[0]
                action = parts[1]
                runtime = ProjectLifecycleRuntime(self.store)
                payload = self._read_optional_json()
                actor = self._founder_id()
                if action == "update":
                    self._send_json(200, runtime.update(project_id, payload, actor=actor))
                    return
                if action == "archive":
                    reason = payload.get("reason", "archived by founder")
                    if not isinstance(reason, str):
                        raise bad_request("reason must be a string")
                    self._send_json(200, runtime.archive(project_id, actor=actor, reason=reason))
                    return
                if action == "restore":
                    self._send_json(200, runtime.restore(project_id, actor=actor))
                    return
                if action == "duplicate":
                    title = payload.get("title")
                    if title is not None and not isinstance(title, str):
                        raise bad_request("title must be a string")
                    self._send_json(201, runtime.duplicate(project_id, actor=actor, title=title))
                    return
                if action == "validate-readiness":
                    self._send_json(200, runtime.validate_readiness(project_id, actor=actor))
                    return
            if parsed.path.startswith("/projects/") and parsed.path.endswith("/product-definition"):
                project_id = parsed.path.removeprefix("/projects/").removesuffix("/product-definition").strip("/")
                if not project_id:
                    raise bad_request("Project ID is required")
                payload = self._read_optional_json()
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).run_product_definition(project_id, approval_mode=approval_mode)
                self._send_json(201, result)
                return
            if parsed.path.startswith("/workflows/") and parsed.path.endswith("/retry"):
                workflow_id = parsed.path.removeprefix("/workflows/").removesuffix("/retry").strip("/")
                if not workflow_id:
                    raise bad_request("Workflow ID is required")
                self._send_json(200, {"workflow": WorkflowEngine(self.store).retry(workflow_id)})
                return
            if parsed.path.startswith("/workflows/") and parsed.path.endswith("/pause"):
                workflow_id = parsed.path.removeprefix("/workflows/").removesuffix("/pause").strip("/")
                if not workflow_id:
                    raise bad_request("Workflow ID is required")
                payload = self._read_optional_json()
                reason = payload.get("reason", "manual pause")
                if not isinstance(reason, str):
                    raise bad_request("reason must be a string")
                self._send_json(200, GenesisOrchestrator(self.store).pause_workflow(workflow_id, reason=reason))
                return
            if parsed.path.startswith("/workflows/") and parsed.path.endswith("/cancel"):
                workflow_id = parsed.path.removeprefix("/workflows/").removesuffix("/cancel").strip("/")
                if not workflow_id:
                    raise bad_request("Workflow ID is required")
                payload = self._read_optional_json()
                reason = payload.get("reason", "manual cancel")
                if not isinstance(reason, str):
                    raise bad_request("reason must be a string")
                self._send_json(200, GenesisOrchestrator(self.store).cancel_workflow(workflow_id, reason=reason))
                return
            if parsed.path.startswith("/workflows/") and parsed.path.endswith("/resume"):
                workflow_id = parsed.path.removeprefix("/workflows/").removesuffix("/resume").strip("/")
                if not workflow_id:
                    raise bad_request("Workflow ID is required")
                payload = self._read_optional_json()
                approval_mode = payload.get("approvalMode", "auto")
                if not isinstance(approval_mode, str):
                    raise bad_request("approvalMode must be a string")
                result = GenesisOrchestrator(self.store).resume_research_workflow(workflow_id, approval_mode=approval_mode)
                self._send_json(200, result)
                return
            if parsed.path.startswith("/approvals/") and (parsed.path.endswith("/approve") or parsed.path.endswith("/reject")):
                action = "approve" if parsed.path.endswith("/approve") else "reject"
                approval_id = parsed.path.removeprefix("/approvals/").removesuffix(f"/{action}").strip("/")
                if not approval_id:
                    raise bad_request("Approval ID is required")
                payload = self._read_optional_json()
                actor = payload.get("actor", "founder")
                note = payload.get("note")
                if not isinstance(actor, str):
                    raise bad_request("actor must be a string")
                if note is not None and not isinstance(note, str):
                    raise bad_request("note must be a string")
                orchestrator = GenesisOrchestrator(self.store)
                result = orchestrator.approve_gate(approval_id, actor=actor, note=note) if action == "approve" else orchestrator.reject_gate(approval_id, actor=actor, note=note)
                self._send_json(200, result)
                return
            self._send_json(404, {"status": "not_found", "path": parsed.path})
        except GenesisError as exc:
            self._send_json(exc.status_code, exc.to_payload())
        except FileNotFoundError as exc:
            error = not_found(str(exc))
            self._send_json(error.status_code, error.to_payload())
        except ValueError as exc:
            error = bad_request(str(exc))
            self._send_json(error.status_code, error.to_payload())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        logger = getattr(self.server, "runtime_logger", None)
        if logger:
            logger.info(format, *args)


def create_server(config: RuntimeConfig | None = None) -> ThreadingHTTPServer:
    runtime_config = config or load_runtime_config()
    logger = configure_logging(runtime_config.log_level)
    server = ThreadingHTTPServer((runtime_config.api_host, runtime_config.api_port), GenesisApiHandler)
    server.runtime_config = runtime_config  # type: ignore[attr-defined]
    server.runtime_logger = logger  # type: ignore[attr-defined]
    server.store = JsonStore(runtime_config.data_dir)  # type: ignore[attr-defined]
    return server


def main() -> int:
    config = load_runtime_config()
    logger = configure_logging(config.log_level)
    server = create_server(config)
    logger.info("Genesis API starting on %s", config.base_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Genesis API shutdown requested")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

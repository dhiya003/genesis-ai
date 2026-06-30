"""Minimal Genesis AI API runtime with BusinessOS sprint endpoints."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from apps.errors import GenesisError, bad_request, not_found
from apps.observability import summarize_metrics
from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from config import RuntimeConfig, configure_logging, load_runtime_config

API_VERSION = "0.6.0"


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

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        config: RuntimeConfig = self.server.runtime_config  # type: ignore[attr-defined]
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/health":
                self._send_json(200, config.health_payload("api"))
                return
            if parsed.path == "/version":
                self._send_json(200, {"app": config.app_name, "version": API_VERSION, "release": "Sprint 6 - Business Execution & Publishing Engine"})
                return
            if parsed.path == "/metrics":
                metrics = self.store.list_metrics()
                self._send_json(200, {"summary": summarize_metrics(metrics), "metrics": metrics})
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
            if parsed.path.startswith("/projects/"):
                project_id = parsed.path.removeprefix("/projects/").strip("/")
                if not project_id:
                    raise bad_request("Project ID is required")
                try:
                    self._send_json(200, GenesisOrchestrator(self.store).get_project(project_id))
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

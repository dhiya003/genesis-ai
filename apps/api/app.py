"""Minimal Genesis AI API runtime with Sprint 2 research endpoints."""

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

API_VERSION = "0.2.0"


class GenesisApiHandler(BaseHTTPRequestHandler):
    """HTTP handler for Sprint 2 runtime bootstrap and research endpoints."""

    server_version = "GenesisAI/0.2"

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
                self._send_json(200, {"app": config.app_name, "version": API_VERSION, "release": "Sprint 2 - Intelligent Research Engine"})
                return
            if parsed.path == "/metrics":
                metrics = self.store.list_metrics()
                self._send_json(200, {"summary": summarize_metrics(metrics), "metrics": metrics})
                return
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
            self._send_json(404, {"status": "not_found", "path": parsed.path})
        except GenesisError as exc:
            self._send_json(exc.status_code, exc.to_payload())

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        try:
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

"""Genesis AI command-line runtime entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from apps.errors import GenesisError, not_found
from apps.factory.runner import build_launch_pack
from apps.observability import summarize_metrics
from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from apps.worker.main import worker_health
from config import RuntimeConfig, load_runtime_config

CLI_VERSION = "1.0.0-foundation"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genesis AI runtime CLI")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("health", help="Print runtime health as JSON")
    subcommands.add_parser("version", help="Print runtime version as JSON")

    run_parser = subcommands.add_parser("run", help="Build a launch pack from a founder requirement")
    run_parser.add_argument("requirement", help="Plain-text founder requirement or path when --from-file is used")
    run_parser.add_argument("--from-file", action="store_true", help="Read requirement from a text file")

    submit_parser = subcommands.add_parser("submit", help="Submit founder idea and execute research workflow")
    submit_parser.add_argument("idea", help="Plain-text founder idea or path when --from-file is used")
    submit_parser.add_argument("--from-file", action="store_true", help="Read idea from a text file")
    submit_parser.add_argument("--data-dir", help="Override Genesis data directory")
    submit_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="auto", help="Approval gate mode after research")
    submit_parser.add_argument("--country")
    submit_parser.add_argument("--budget")
    submit_parser.add_argument("--timeline")
    submit_parser.add_argument("--constraint", action="append", default=[])

    project_parser = subcommands.add_parser("project", help="Retrieve a stored project with tasks, deliverables, and audit history")
    project_parser.add_argument("project_id")
    project_parser.add_argument("--data-dir", help="Override Genesis data directory")

    report_parser = subcommands.add_parser("report", help="Retrieve a stored research report")
    report_parser.add_argument("project_id", help="Project ID returned by submit")
    report_parser.add_argument("--data-dir", help="Override Genesis data directory")

    product_parser = subcommands.add_parser("product", help="Run and retrieve Sprint 3 Product Department outputs")
    product_subcommands = product_parser.add_subparsers(dest="product_command", required=True)
    product_run_parser = product_subcommands.add_parser("run", help="Run Product Department Phase 1 from a stored research report")
    product_run_parser.add_argument("project_id")
    product_run_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="auto")
    product_run_parser.add_argument("--data-dir")
    product_generate_parser = product_subcommands.add_parser("generate", help="Generate a complete Product Blueprint from a stored research report")
    product_generate_parser.add_argument("project_id")
    product_generate_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="auto")
    product_generate_parser.add_argument("--data-dir")
    product_definition_parser = product_subcommands.add_parser("definition", help="Retrieve a stored product definition")
    product_definition_parser.add_argument("project_id")
    product_definition_parser.add_argument("--data-dir")
    for name in ["blueprint", "bom", "cost", "suppliers", "packaging", "profitability"]:
        section_parser = product_subcommands.add_parser(name, help=f"Retrieve stored product {name}")
        section_parser.add_argument("product_id")
        section_parser.add_argument("--data-dir")

    creative_parser = subcommands.add_parser("creative", help="Run and retrieve Sprint 4 Creative Studio outputs")
    creative_subcommands = creative_parser.add_subparsers(dest="creative_command", required=True)
    creative_generate_parser = creative_subcommands.add_parser("generate", help="Generate a Creative Pack from a stored Product Blueprint")
    creative_generate_parser.add_argument("product_id")
    creative_generate_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="auto")
    creative_generate_parser.add_argument("--data-dir")
    for name in ["pack", "brand", "logo", "packaging", "mockups", "marketplace", "social", "copy", "assets"]:
        section_parser = creative_subcommands.add_parser(name, help=f"Retrieve stored creative {name}")
        section_parser.add_argument("creative_id")
        section_parser.add_argument("--data-dir")

    marketing_parser = subcommands.add_parser("marketing", help="Run and retrieve Sprint 5 Marketing Engine outputs")
    marketing_subcommands = marketing_parser.add_subparsers(dest="marketing_command", required=True)
    marketing_generate_parser = marketing_subcommands.add_parser("generate", help="Generate a Marketing Pack from a stored Creative Pack")
    marketing_generate_parser.add_argument("creative_id")
    marketing_generate_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="auto")
    marketing_generate_parser.add_argument("--data-dir")
    for name in ["pack", "strategy", "seo", "social", "ads", "listing", "launch"]:
        section_parser = marketing_subcommands.add_parser(name, help=f"Retrieve stored marketing {name}")
        section_parser.add_argument("marketing_id")
        section_parser.add_argument("--data-dir")

    launch_parser = subcommands.add_parser("launch", help="Run and retrieve Sprint 6 Business Execution outputs")
    launch_subcommands = launch_parser.add_subparsers(dest="launch_command", required=True)
    launch_generate_parser = launch_subcommands.add_parser("generate", help="Generate a Business Launch Package from a stored Marketing Pack")
    launch_generate_parser.add_argument("marketing_id")
    launch_generate_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="manual")
    launch_generate_parser.add_argument("--data-dir")
    for name in ["package", "status", "assets", "report", "checklist"]:
        section_parser = launch_subcommands.add_parser(name, help=f"Retrieve stored launch {name}")
        section_parser.add_argument("launch_id")
        section_parser.add_argument("--data-dir")

    businessos_parser = subcommands.add_parser("businessos", help="Run and retrieve Sprint 8 BusinessOS outputs")
    businessos_subcommands = businessos_parser.add_subparsers(dest="businessos_command", required=True)
    businessos_generate_parser = businessos_subcommands.add_parser("generate", help="Generate a Business Operating Plan from a stored Business Launch Package")
    businessos_generate_parser.add_argument("launch_id")
    businessos_generate_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="manual")
    businessos_generate_parser.add_argument("--data-dir")
    businessos_metrics_parser = businessos_subcommands.add_parser("ingest-metrics", help="Ingest a business metrics JSON object and refresh dashboards")
    businessos_metrics_parser.add_argument("business_id")
    businessos_metrics_parser.add_argument("metrics", help="JSON metrics object or path when --from-file is used")
    businessos_metrics_parser.add_argument("--from-file", action="store_true")
    businessos_metrics_parser.add_argument("--source", default="manual")
    businessos_metrics_parser.add_argument("--observed-at")
    businessos_metrics_parser.add_argument("--data-dir")
    for name in ["plan", "digital-twin", "knowledge-graph", "decisions", "simulations", "health", "recommendations", "dashboard", "alerts", "knowledge", "metrics"]:
        section_parser = businessos_subcommands.add_parser(name, help=f"Retrieve stored BusinessOS {name}")
        section_parser.add_argument("business_id")
        section_parser.add_argument("--data-dir")

    drive_parser = subcommands.add_parser("drive", help="Google Drive integration utilities")
    drive_subcommands = drive_parser.add_subparsers(dest="drive_command", required=True)
    drive_upload_parser = drive_subcommands.add_parser("upload", help="Upload a local file to Google Drive")
    drive_upload_parser.add_argument("path")
    drive_upload_parser.add_argument("--name")
    drive_upload_parser.add_argument("--mime-type")

    workflow_parser = subcommands.add_parser("workflow", help="Manage stored workflows")
    workflow_subcommands = workflow_parser.add_subparsers(dest="workflow_command", required=True)
    pause_parser = workflow_subcommands.add_parser("pause", help="Pause an active workflow")
    pause_parser.add_argument("workflow_id")
    pause_parser.add_argument("--reason", default="manual pause")
    pause_parser.add_argument("--data-dir")
    cancel_parser = workflow_subcommands.add_parser("cancel", help="Cancel an incomplete workflow")
    cancel_parser.add_argument("workflow_id")
    cancel_parser.add_argument("--reason", default="manual cancel")
    cancel_parser.add_argument("--data-dir")

    resume_parser = subcommands.add_parser("resume", help="Resume a stored research workflow")
    resume_parser.add_argument("workflow_id", help="Workflow ID returned by submit")
    resume_parser.add_argument("--approval-mode", choices=["auto", "manual", "human"], default="auto", help="Approval gate mode if resume completes research")
    resume_parser.add_argument("--data-dir", help="Override Genesis data directory")

    approval_parser = subcommands.add_parser("approval", help="Approve or reject a pending approval gate")
    approval_subcommands = approval_parser.add_subparsers(dest="approval_command", required=True)
    approve_parser = approval_subcommands.add_parser("approve", help="Approve a pending gate")
    approve_parser.add_argument("approval_id")
    approve_parser.add_argument("--actor", default="founder")
    approve_parser.add_argument("--note")
    approve_parser.add_argument("--data-dir")
    reject_parser = approval_subcommands.add_parser("reject", help="Reject a pending gate")
    reject_parser.add_argument("approval_id")
    reject_parser.add_argument("--actor", default="founder")
    reject_parser.add_argument("--note")
    reject_parser.add_argument("--data-dir")

    metrics_parser = subcommands.add_parser("metrics", help="List persisted runtime metrics")
    metrics_parser.add_argument("--limit", type=int)
    metrics_parser.add_argument("--data-dir", help="Override Genesis data directory")
    return parser


def health(config: RuntimeConfig | None = None) -> dict[str, object]:
    runtime_config = config or load_runtime_config()
    return {
        "status": "ok",
        "api": runtime_config.health_payload("api"),
        "worker": worker_health(runtime_config),
    }


def _read_text_arg(value: str, from_file: bool) -> str:
    if not from_file:
        return value
    return Path(value).read_text(encoding="utf-8")


def _store(data_dir: str | None = None) -> JsonStore:
    config = load_runtime_config()
    return JsonStore(data_dir or config.data_dir)


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "health":
            _print_json(health())
            return 0
        if args.command == "version":
            config = load_runtime_config()
            _print_json({"app": config.app_name, "version": CLI_VERSION, "release": "Sprint 8 - Genesis BusinessOS Foundation"})
            return 0
        if args.command == "run":
            requirement = _read_text_arg(args.requirement, args.from_file)
            _print_json(build_launch_pack(requirement))
            return 0
        if args.command == "submit":
            idea = _read_text_arg(args.idea, args.from_file)
            result = GenesisOrchestrator(_store(args.data_dir)).submit_idea(
                idea,
                approval_mode=args.approval_mode,
                country=args.country,
                budget=args.budget,
                timeline=args.timeline,
                constraints=args.constraint,
            )
            _print_json(result)
            return 0
        if args.command == "project":
            try:
                _print_json(GenesisOrchestrator(_store(args.data_dir)).get_project(args.project_id))
            except FileNotFoundError as exc:
                raise not_found(f"Project not found: {args.project_id}") from exc
            return 0
        if args.command == "workflow":
            orchestrator = GenesisOrchestrator(_store(args.data_dir))
            if args.workflow_command == "pause":
                _print_json(orchestrator.pause_workflow(args.workflow_id, reason=args.reason))
                return 0
            if args.workflow_command == "cancel":
                _print_json(orchestrator.cancel_workflow(args.workflow_id, reason=args.reason))
                return 0
        if args.command == "resume":
            result = GenesisOrchestrator(_store(args.data_dir)).resume_research_workflow(args.workflow_id, approval_mode=args.approval_mode)
            _print_json(result)
            return 0
        if args.command == "report":
            store = _store(args.data_dir)
            try:
                report = store.get_report(args.project_id)
            except FileNotFoundError as exc:
                raise not_found(f"Research report not found for project {args.project_id}") from exc
            _print_json(report)
            return 0
        if args.command == "product":
            orchestrator = GenesisOrchestrator(_store(args.data_dir))
            if args.product_command == "run":
                try:
                    _print_json(orchestrator.run_product_definition(args.project_id, approval_mode=args.approval_mode))
                except FileNotFoundError as exc:
                    raise not_found(f"Project or research report not found for project {args.project_id}") from exc
                return 0
            if args.product_command == "generate":
                try:
                    _print_json(orchestrator.generate_product_blueprint(args.project_id, approval_mode=args.approval_mode))
                except FileNotFoundError as exc:
                    raise not_found(f"Project or research report not found for project {args.project_id}") from exc
                return 0
            if args.product_command == "definition":
                try:
                    _print_json(orchestrator.get_product_definition(args.project_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Product definition not found for project {args.project_id}") from exc
                return 0
            if args.product_command == "blueprint":
                _print_json(orchestrator.get_product_blueprint(args.product_id))
                return 0
            if args.product_command == "bom":
                _print_json(orchestrator.get_product_bom(args.product_id))
                return 0
            if args.product_command == "cost":
                _print_json(orchestrator.get_product_cost(args.product_id))
                return 0
            if args.product_command == "suppliers":
                _print_json(orchestrator.get_product_suppliers(args.product_id))
                return 0
            if args.product_command == "packaging":
                _print_json(orchestrator.get_product_packaging(args.product_id))
                return 0
            if args.product_command == "profitability":
                _print_json(orchestrator.get_product_profitability(args.product_id))
                return 0
        if args.command == "creative":
            orchestrator = GenesisOrchestrator(_store(args.data_dir))
            if args.creative_command == "generate":
                try:
                    _print_json(orchestrator.generate_creative_pack(args.product_id, approval_mode=args.approval_mode))
                except FileNotFoundError as exc:
                    raise not_found(f"Product Blueprint not found for product {args.product_id}") from exc
                return 0
            if args.creative_command == "pack":
                _print_json(orchestrator.get_creative_pack(args.creative_id))
                return 0
            if args.creative_command == "brand":
                _print_json(orchestrator.get_creative_brand(args.creative_id))
                return 0
            if args.creative_command == "logo":
                _print_json(orchestrator.get_creative_logo(args.creative_id))
                return 0
            if args.creative_command == "packaging":
                _print_json(orchestrator.get_creative_packaging(args.creative_id))
                return 0
            if args.creative_command == "mockups":
                _print_json(orchestrator.get_creative_mockups(args.creative_id))
                return 0
            if args.creative_command == "marketplace":
                _print_json(orchestrator.get_creative_marketplace(args.creative_id))
                return 0
            if args.creative_command == "social":
                _print_json(orchestrator.get_creative_social(args.creative_id))
                return 0
            if args.creative_command == "copy":
                _print_json(orchestrator.get_creative_copy(args.creative_id))
                return 0
            if args.creative_command == "assets":
                _print_json(orchestrator.get_creative_assets(args.creative_id))
                return 0
        if args.command == "marketing":
            orchestrator = GenesisOrchestrator(_store(args.data_dir))
            if args.marketing_command == "generate":
                try:
                    _print_json(orchestrator.generate_marketing_pack(args.creative_id, approval_mode=args.approval_mode))
                except FileNotFoundError as exc:
                    raise not_found(f"Creative Pack not found for creative {args.creative_id}") from exc
                return 0
            if args.marketing_command == "pack":
                _print_json(orchestrator.get_marketing_pack(args.marketing_id))
                return 0
            if args.marketing_command == "strategy":
                _print_json(orchestrator.get_marketing_strategy(args.marketing_id))
                return 0
            if args.marketing_command == "seo":
                _print_json(orchestrator.get_marketing_seo(args.marketing_id))
                return 0
            if args.marketing_command == "social":
                _print_json(orchestrator.get_marketing_social(args.marketing_id))
                return 0
            if args.marketing_command == "ads":
                _print_json(orchestrator.get_marketing_ads(args.marketing_id))
                return 0
            if args.marketing_command == "listing":
                _print_json(orchestrator.get_marketing_listing(args.marketing_id))
                return 0
            if args.marketing_command == "launch":
                _print_json(orchestrator.get_marketing_launch(args.marketing_id))
                return 0
        if args.command == "drive":
            from apps.integrations.google_drive import GoogleDriveClient, google_drive_config_from_env

            if args.drive_command == "upload":
                client = GoogleDriveClient(google_drive_config_from_env())
                _print_json(client.upload_file(Path(args.path), name=args.name, mime_type=args.mime_type))
                return 0
        if args.command == "launch":
            orchestrator = GenesisOrchestrator(_store(args.data_dir))
            if args.launch_command == "generate":
                try:
                    _print_json(orchestrator.generate_business_launch_package(args.marketing_id, approval_mode=args.approval_mode))
                except FileNotFoundError as exc:
                    raise not_found(f"Marketing Pack not found for marketing {args.marketing_id}") from exc
                return 0
            if args.launch_command == "package":
                _print_json(orchestrator.get_business_launch_package(args.launch_id))
                return 0
            if args.launch_command == "status":
                _print_json(orchestrator.get_business_launch_status(args.launch_id))
                return 0
            if args.launch_command == "assets":
                _print_json(orchestrator.get_business_launch_assets(args.launch_id))
                return 0
            if args.launch_command == "report":
                _print_json(orchestrator.get_business_launch_report(args.launch_id))
                return 0
            if args.launch_command == "checklist":
                _print_json(orchestrator.get_business_launch_checklist(args.launch_id))
                return 0
        if args.command == "businessos":
            orchestrator = GenesisOrchestrator(_store(args.data_dir))
            if args.businessos_command == "generate":
                try:
                    _print_json(orchestrator.generate_business_operating_plan(args.launch_id, approval_mode=args.approval_mode))
                except FileNotFoundError as exc:
                    raise not_found(f"Business Launch Package not found for launch {args.launch_id}") from exc
                return 0
            if args.businessos_command == "ingest-metrics":
                metrics_text = _read_text_arg(args.metrics, args.from_file)
                metrics = json.loads(metrics_text)
                if not isinstance(metrics, dict):
                    raise ValueError("metrics must be a JSON object")
                _print_json(orchestrator.ingest_business_metrics(args.business_id, metrics, source=args.source, observed_at=args.observed_at))
                return 0
            if args.businessos_command == "plan":
                _print_json(orchestrator.get_business_operating_plan(args.business_id))
                return 0
            if args.businessos_command == "digital-twin":
                _print_json(orchestrator.get_digital_twin(args.business_id))
                return 0
            if args.businessos_command == "knowledge-graph":
                _print_json(orchestrator.get_knowledge_graph(args.business_id))
                return 0
            if args.businessos_command == "decisions":
                _print_json(orchestrator.get_decisions(args.business_id))
                return 0
            if args.businessos_command == "simulations":
                _print_json(orchestrator.get_simulations(args.business_id))
                return 0
            if args.businessos_command == "health":
                _print_json(orchestrator.get_business_health(args.business_id))
                return 0
            if args.businessos_command == "recommendations":
                _print_json(orchestrator.get_recommendations(args.business_id))
                return 0
            if args.businessos_command == "dashboard":
                _print_json(orchestrator.get_business_dashboard(args.business_id))
                return 0
            if args.businessos_command == "alerts":
                _print_json(orchestrator.get_business_alerts(args.business_id))
                return 0
            if args.businessos_command == "knowledge":
                _print_json(orchestrator.get_business_knowledge(args.business_id))
                return 0
            if args.businessos_command == "metrics":
                _print_json(orchestrator.list_business_metric_events(args.business_id))
                return 0
        if args.command == "approval":
            orchestrator = GenesisOrchestrator(_store(args.data_dir))
            if args.approval_command == "approve":
                _print_json(orchestrator.approve_gate(args.approval_id, actor=args.actor, note=args.note))
                return 0
            if args.approval_command == "reject":
                _print_json(orchestrator.reject_gate(args.approval_id, actor=args.actor, note=args.note))
                return 0
        if args.command == "metrics":
            metrics = _store(args.data_dir).list_metrics(limit=args.limit)
            _print_json({"summary": summarize_metrics(metrics), "metrics": metrics})
            return 0
    except GenesisError as exc:
        _print_json(exc.to_payload())
        return 1
    except ValueError as exc:
        _print_json({"error": {"code": "BAD_REQUEST", "message": str(exc)}})
        return 1
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

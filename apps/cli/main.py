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

CLI_VERSION = "0.3.0"


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
    product_definition_parser = product_subcommands.add_parser("definition", help="Retrieve a stored product definition")
    product_definition_parser.add_argument("project_id")
    product_definition_parser.add_argument("--data-dir")

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
            _print_json({"app": config.app_name, "version": CLI_VERSION, "release": "Sprint 3 - Product Intelligence & Engineering"})
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
            if args.product_command == "definition":
                try:
                    _print_json(orchestrator.get_product_definition(args.project_id))
                except FileNotFoundError as exc:
                    raise not_found(f"Product definition not found for project {args.project_id}") from exc
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

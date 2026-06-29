"""Genesis AI command-line runtime entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from apps.errors import GenesisError, not_found
from apps.factory.runner import build_launch_pack
from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from apps.worker.main import worker_health
from config import RuntimeConfig, load_runtime_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genesis AI runtime CLI")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("health", help="Print runtime health as JSON")

    run_parser = subcommands.add_parser("run", help="Build a launch pack from a founder requirement")
    run_parser.add_argument("requirement", help="Plain-text founder requirement or path when --from-file is used")
    run_parser.add_argument("--from-file", action="store_true", help="Read requirement from a text file")

    submit_parser = subcommands.add_parser("submit", help="Submit founder idea and execute research workflow")
    submit_parser.add_argument("idea", help="Plain-text founder idea or path when --from-file is used")
    submit_parser.add_argument("--from-file", action="store_true", help="Read idea from a text file")
    submit_parser.add_argument("--data-dir", help="Override Genesis data directory")

    report_parser = subcommands.add_parser("report", help="Retrieve a stored research report")
    report_parser.add_argument("project_id", help="Project ID returned by submit")
    report_parser.add_argument("--data-dir", help="Override Genesis data directory")
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
        if args.command == "run":
            requirement = _read_text_arg(args.requirement, args.from_file)
            _print_json(build_launch_pack(requirement))
            return 0
        if args.command == "submit":
            idea = _read_text_arg(args.idea, args.from_file)
            result = GenesisOrchestrator(_store(args.data_dir)).submit_idea(idea)
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

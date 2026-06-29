"""Genesis AI command-line runtime entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from apps.factory.runner import build_launch_pack
from apps.worker.main import worker_health
from config import RuntimeConfig, load_runtime_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genesis AI runtime CLI")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("health", help="Print runtime health as JSON")

    run_parser = subcommands.add_parser("run", help="Build a launch pack from a founder requirement")
    run_parser.add_argument("requirement", help="Plain-text founder requirement or path when --from-file is used")
    run_parser.add_argument("--from-file", action="store_true", help="Read requirement from a text file")
    return parser


def health(config: RuntimeConfig | None = None) -> dict[str, object]:
    runtime_config = config or load_runtime_config()
    return {
        "status": "ok",
        "api": runtime_config.health_payload("api"),
        "worker": worker_health(runtime_config),
    }


def _read_requirement(value: str, from_file: bool) -> str:
    if not from_file:
        return value
    return Path(value).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "health":
        print(json.dumps(health(), sort_keys=True))
        return 0
    if args.command == "run":
        requirement = _read_requirement(args.requirement, args.from_file)
        print(json.dumps(build_launch_pack(requirement), indent=2, sort_keys=True))
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

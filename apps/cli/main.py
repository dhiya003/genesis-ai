"""Genesis AI command-line runtime entrypoint."""

from __future__ import annotations

import argparse
import json

from apps.worker.main import worker_health
from config import RuntimeConfig, load_runtime_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genesis AI runtime CLI")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("health", help="Print runtime health as JSON")
    return parser


def health(config: RuntimeConfig | None = None) -> dict[str, object]:
    runtime_config = config or load_runtime_config()
    return {
        "status": "ok",
        "api": runtime_config.health_payload("api"),
        "worker": worker_health(runtime_config),
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "health":
        print(json.dumps(health(), sort_keys=True))
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

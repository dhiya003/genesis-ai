"""Genesis AI worker runtime bootstrap."""

from __future__ import annotations

from config import RuntimeConfig, configure_logging, load_runtime_config


def worker_health(config: RuntimeConfig | None = None) -> dict[str, str]:
    runtime_config = config or load_runtime_config()
    payload = runtime_config.health_payload("worker")
    payload["queue"] = runtime_config.worker_queue_name
    return payload


def main() -> int:
    config = load_runtime_config()
    logger = configure_logging(config.log_level)
    logger.info("Genesis worker ready for queue %s", config.worker_queue_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Runtime configuration for Genesis AI.

The runtime bootstrap intentionally uses Python's standard library only so
Sprint 2 can keep CI lean and avoid paid/cloud infrastructure dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


@dataclass(frozen=True)
class RuntimeConfig:
    """Validated runtime settings shared by API, worker, and CLI processes."""

    app_name: str = "genesis-ai"
    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    worker_queue_name: str = "manual-launch-pack"
    data_dir: str = ".genesis-data"
    auth_mode: str = "off"
    api_keys: str = ""
    tenant_id: str = "default-org"
    require_tenant_header: bool = False

    @property
    def base_url(self) -> str:
        return f"http://{self.api_host}:{self.api_port}"

    def health_payload(self, component: str) -> dict[str, str]:
        return {
            "status": "ok",
            "app": self.app_name,
            "component": component,
            "environment": self.environment,
        }


def _read_int(env: Mapping[str, str], key: str, default: int) -> int:
    raw_value = env.get(key)
    if raw_value in (None, ""):
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{key} must be an integer") from exc
    if not 0 < value < 65536:
        raise ValueError(f"{key} must be between 1 and 65535")
    return value


def _read_bool(env: Mapping[str, str], key: str, default: bool) -> bool:
    raw_value = env.get(key)
    if raw_value in (None, ""):
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{key} must be a boolean")


def load_runtime_config(env: Mapping[str, str] | None = None) -> RuntimeConfig:
    """Load runtime settings from environment variables.

    Defaults are safe for local execution and CI. Real secrets are deliberately
    excluded from this bootstrap layer.
    """

    source = os.environ if env is None else env
    return RuntimeConfig(
        app_name=source.get("GENESIS_APP_NAME", "genesis-ai"),
        environment=source.get("GENESIS_ENV", "development"),
        log_level=source.get("GENESIS_LOG_LEVEL", "INFO").upper(),
        api_host=source.get("GENESIS_API_HOST", "127.0.0.1"),
        api_port=_read_int(source, "GENESIS_API_PORT", 8000),
        worker_queue_name=source.get("GENESIS_WORKER_QUEUE", "manual-launch-pack"),
        data_dir=source.get("GENESIS_DATA_DIR", ".genesis-data"),
        auth_mode=source.get("GENESIS_AUTH_MODE", "off").lower(),
        api_keys=source.get("GENESIS_API_KEYS", ""),
        tenant_id=source.get("GENESIS_TENANT_ID", "default-org"),
        require_tenant_header=_read_bool(source, "GENESIS_REQUIRE_TENANT_HEADER", False),
    )

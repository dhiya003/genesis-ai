"""API-key authentication, RBAC, and tenant guardrails."""

from __future__ import annotations

from dataclasses import dataclass
import hmac
from http.client import HTTPMessage

from apps.errors import forbidden, unauthorized
from config import RuntimeConfig


PUBLIC_AUTH_OFF_ROLE = "founder"


@dataclass(frozen=True)
class ApiPrincipal:
    """Authenticated caller context used by API handlers."""

    role: str
    tenant_id: str
    auth_mode: str


def authenticate_request(headers: HTTPMessage, config: RuntimeConfig, allowed_roles: set[str]) -> ApiPrincipal:
    """Authenticate a request and enforce role + tenant boundaries.

    `GENESIS_AUTH_MODE=off` keeps local development and CI frictionless.
    `GENESIS_AUTH_MODE=api_key` expects `Authorization: Bearer <key>` or
    `X-Genesis-Api-Key: <key>`, with `GENESIS_API_KEYS` formatted as
    `founder=key-one,operator=key-two,viewer=key-three`.
    """

    if config.auth_mode in {"", "off", "none", "disabled"}:
        return ApiPrincipal(role=PUBLIC_AUTH_OFF_ROLE, tenant_id=config.tenant_id, auth_mode="off")
    if config.auth_mode != "api_key":
        raise unauthorized(f"Unsupported auth mode: {config.auth_mode}")

    role = _role_for_key(_request_key(headers), _parse_api_keys(config.api_keys))
    if role is None:
        raise unauthorized("A valid Genesis API key is required")
    if role not in allowed_roles:
        raise forbidden(f"Role '{role}' is not allowed for this operation")

    tenant_id = headers.get("X-Genesis-Tenant-ID")
    if config.require_tenant_header and not tenant_id:
        raise forbidden("X-Genesis-Tenant-ID header is required")
    if tenant_id and tenant_id != config.tenant_id:
        raise forbidden("Request tenant does not match configured tenant")
    return ApiPrincipal(role=role, tenant_id=tenant_id or config.tenant_id, auth_mode="api_key")


def _request_key(headers: HTTPMessage) -> str:
    authorization = headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return headers.get("X-Genesis-Api-Key", "").strip()


def _parse_api_keys(raw_keys: str) -> dict[str, str]:
    registry: dict[str, str] = {}
    for item in raw_keys.split(","):
        if not item.strip() or "=" not in item:
            continue
        role, key = item.split("=", 1)
        normalized_role = role.strip().lower()
        normalized_key = key.strip()
        if normalized_role and normalized_key:
            registry[normalized_role] = normalized_key
    return registry


def _role_for_key(candidate: str, registry: dict[str, str]) -> str | None:
    if not candidate:
        return None
    for role, stored_key in registry.items():
        if hmac.compare_digest(candidate, stored_key):
            return role
    return None

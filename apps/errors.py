"""Standard Genesis error payloads."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenesisError(Exception):
    """Application error rendered consistently by API and CLI callers."""

    code: str
    message: str
    status_code: int = 400

    def to_payload(self) -> dict[str, object]:
        return {"error": {"code": self.code, "message": self.message}}


def not_found(message: str) -> GenesisError:
    return GenesisError(code="NOT_FOUND", message=message, status_code=404)


def bad_request(message: str) -> GenesisError:
    return GenesisError(code="BAD_REQUEST", message=message, status_code=400)


def unauthorized(message: str) -> GenesisError:
    return GenesisError(code="UNAUTHORIZED", message=message, status_code=401)


def forbidden(message: str) -> GenesisError:
    return GenesisError(code="FORBIDDEN", message=message, status_code=403)

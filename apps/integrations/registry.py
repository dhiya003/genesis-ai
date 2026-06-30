"""Sanitized integration readiness registry for production BusinessOS work."""

from __future__ import annotations

import os
from typing import Mapping


INTEGRATIONS: dict[str, dict[str, object]] = {
    "openai": {"category": "ai", "requiredEnv": ["OPENAI_API_KEY"], "implemented": True},
    "serpapi": {"category": "market_research", "requiredEnv": ["SERPAPI_API_KEY"], "implemented": True},
    "google_drive": {"category": "asset_export", "requiredEnv": ["GOOGLE_DRIVE_ACCESS_TOKEN"], "implemented": True},
    "shopify": {"category": "store", "requiredEnv": ["SHOPIFY_STORE_URL", "SHOPIFY_ACCESS_TOKEN"], "implemented": False},
    "meta": {"category": "social_ads", "requiredEnv": ["META_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ACCOUNT_ID", "FACEBOOK_PAGE_ID"], "implemented": False},
    "amazon_seller": {"category": "marketplace", "requiredEnv": ["AMAZON_SELLER_PARTNER_APP_ID", "AMAZON_SELLER_PARTNER_REFRESH_TOKEN"], "implemented": False},
    "whatsapp": {"category": "messaging", "requiredEnv": ["WHATSAPP_BUSINESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"], "implemented": False},
    "email": {"category": "crm", "requiredEnv": ["SENDGRID_API_KEY"], "implemented": False},
    "accounting": {"category": "finance", "requiredEnv": ["ACCOUNTING_API_KEY"], "implemented": False},
    "erp": {"category": "operations", "requiredEnv": ["ERP_API_KEY"], "implemented": False},
}


def integration_status(env: Mapping[str, str] | None = None) -> dict[str, object]:
    """Return readiness without leaking credential values."""

    source = os.environ if env is None else env
    providers = []
    for name, definition in sorted(INTEGRATIONS.items()):
        required_env = list(definition["requiredEnv"])  # type: ignore[index]
        configured = [key for key in required_env if bool(source.get(key))]
        missing = [key for key in required_env if not source.get(key)]
        implemented = bool(definition["implemented"])
        if implemented and not missing:
            status = "READY"
        elif implemented:
            status = "MISSING_CREDENTIALS"
        elif not missing:
            status = "CREDENTIALS_PRESENT_CONNECTOR_PENDING"
        else:
            status = "PLANNED"
        providers.append(
            {
                "name": name,
                "category": definition["category"],
                "implemented": implemented,
                "status": status,
                "configuredEnvCount": len(configured),
                "requiredEnv": required_env,
                "missingEnv": missing,
            }
        )
    return {
        "reportType": "INTEGRATION_READINESS",
        "providers": providers,
        "summary": {
            "ready": sum(1 for provider in providers if provider["status"] == "READY"),
            "implemented": sum(1 for provider in providers if provider["implemented"]),
            "planned": sum(1 for provider in providers if not provider["implemented"]),
            "total": len(providers),
        },
        "secretPolicy": "Only environment variable names and counts are reported. Secret values are never returned.",
    }

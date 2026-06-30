# Sprint 2 Research Provider Guide

Sprint 2 supports three research execution modes.

## Deterministic mode

This is the default mode used by CI and local development.

```bash
export GENESIS_RESEARCH_PROVIDER=deterministic
python scripts/verify.py
```

It executes EMP-001 to EMP-004 locally without secrets or paid APIs.

## Live web mode

This mode enables web-backed market research. By default it uses a lightweight
public search client. If `SERPAPI_API_KEY` is present, Genesis uses SerpAPI as
the governed Google Search backend.

```bash
export GENESIS_RESEARCH_PROVIDER=live_web
python -m apps.cli.main submit "Create a coffee lovers product brand for India."
```

To force SerpAPI:

```bash
export GENESIS_RESEARCH_PROVIDER=live_web
export GENESIS_SEARCH_PROVIDER=serpapi
export SERPAPI_API_KEY=<your-key>
python -m apps.cli.main submit "Create a coffee lovers product brand for India."
```

Live web mode attaches evidence to every employee output:

- EMP-001: trend evidence
- EMP-002: competitor evidence
- EMP-003: customer demand evidence
- EMP-004: product opportunity evidence

Live web mode is not the default CI provider because public search can be unavailable, rate-limited, or blocked by network policy. CI remains deterministic so the build is stable.

## Marketplace mode

Marketplace mode runs source-targeted searches for marketplace and social evidence. It also uses SerpAPI automatically when `SERPAPI_API_KEY` is configured.

```bash
export GENESIS_RESEARCH_PROVIDER=marketplace
export SERPAPI_API_KEY=<your-key>
python -m apps.cli.main submit "Create a coffee lovers product brand for India."
```

## OpenAI mode

This mode enables optional AI-backed research employees.

```bash
export GENESIS_RESEARCH_PROVIDER=openai
export GENESIS_RESEARCH_MODEL=gpt-4.1-mini
export OPENAI_API_KEY=<your-key>
python -m apps.cli.main submit "Create a coffee lovers product brand for India."
```

OpenAI mode is intentionally not required by CI because CI should not depend on paid APIs or secrets.

## Validation

Research reports can be validated with:

```bash
python scripts/validate_research_report.py
```

The Research Department also validates the combined report before storing it.

## Integration boundary

Sprint 2 now supports a live web provider, but marketplace-specific integrations such as Amazon, Instagram, Facebook, Shopify, and WhatsApp still require dedicated API connectors, credentials, rate-limit policies, and compliance controls.

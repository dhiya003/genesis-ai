# Sprint 2 Research Provider Guide

Sprint 2 supports two research execution modes.

## Deterministic mode

This is the default mode used by CI and local development.

```bash
export GENESIS_RESEARCH_PROVIDER=deterministic
python scripts/verify.py
```

It executes EMP-001 to EMP-004 locally without secrets or paid APIs.

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

Sprint 2 completes the executable Product Factory vertical slice. Live marketplace, Instagram, Amazon, and web research are not enabled by default because they require external APIs, credentials, rate-limit policies, and compliance controls.

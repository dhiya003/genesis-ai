# Render Private Alpha

This runbook deploys Genesis as a private alpha API on Render.

## What This Enables

- Docker-based Render web service.
- Public health check at `/health`.
- Protected Genesis API endpoints with API-key authentication.
- Tenant isolation through `X-Genesis-Tenant-ID`.
- Deterministic Sprint 2-8 workflows for safe alpha testing.
- No live marketplace publishing, ad spend, or external write integrations by default.

## Safety Rules

- Do not commit API keys, OAuth secrets, or provider credentials.
- Rotate any key that was pasted into chat before using it in production.
- Keep `GENESIS_RESEARCH_PROVIDER=deterministic` until live research credentials are intentionally enabled.
- Keep `GENESIS_CREATIVE_IMAGE_PROVIDER=deterministic` until image generation/export providers are intentionally enabled.
- Treat the free Render plan as non-durable: data stored in `/tmp/genesis-data` can be lost on restart or deploy.

## Deploy Steps

1. Open Render and create a new Blueprint from the GitHub repository.
2. Select `dhiya003/genesis-ai`.
3. Render will read `render.yaml` and create `genesis-ai-private-alpha`.
4. Add `GENESIS_API_KEYS` as a secret environment variable.
5. Deploy the service.
6. Confirm the service responds at `/health`.

Use this API-key format:

```text
founder=<long-random-founder-key>,operator=<long-random-operator-key>,viewer=<long-random-viewer-key>
```

Generate long random values locally and store them only in Render secrets or a password manager.

## Required Render Environment

The Blueprint sets these values:

```text
GENESIS_ENV=private-alpha
GENESIS_API_HOST=0.0.0.0
GENESIS_DATA_DIR=/tmp/genesis-data
GENESIS_AUTH_MODE=api_key
GENESIS_TENANT_ID=genesis-private-alpha
GENESIS_REQUIRE_TENANT_HEADER=true
GENESIS_RESEARCH_PROVIDER=deterministic
GENESIS_CREATIVE_IMAGE_PROVIDER=deterministic
```

Render provides `PORT` automatically. Genesis falls back to that value when `GENESIS_API_PORT` is not set.

## Smoke Tests

Health check:

```bash
curl -fsS https://<render-service-url>/health
```

Authenticated version check:

```bash
curl -fsS https://<render-service-url>/version \
  -H "Authorization: Bearer <founder-key>" \
  -H "X-Genesis-Tenant-ID: genesis-private-alpha"
```

Private-alpha endpoints require both a valid key and the tenant header.

## Optional Live Credentials Later

Add these only after rotating secrets and deciding to enable live provider behavior:

```text
OPENAI_API_KEY=<rotated-openai-key>
SERPAPI_API_KEY=<rotated-serpapi-key>
GOOGLE_CLIENT_ID=<google-oauth-client-id>
GOOGLE_CLIENT_SECRET=<google-oauth-client-secret>
```

Provider credentials alone do not make Genesis production-ready. Before enabling live execution, add durable storage, backup policy, monitoring, rate limits, and integration-specific approval gates.

## Durable Alpha Upgrade

For a longer private alpha, upgrade the Render service to a paid plan and add a persistent disk mounted at:

```text
/var/data/genesis
```

Then set:

```text
GENESIS_DATA_DIR=/var/data/genesis
```

For production, prefer managed Postgres and object storage over local JSON files.

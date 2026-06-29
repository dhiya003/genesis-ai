# Sprint 2 Run Guide

Sprint 2 Definition of Done requires an executable Product Factory vertical slice:

Founder idea → project created → orchestrator starts workflow → Research Department executes → EMP-001 to EMP-004 run → Research Report generated → report stored → report retrievable through API/CLI → tests and CI pass.

## Verify everything

```bash
python scripts/verify.py
```

This runs:

- repository file checks
- JSON syntax checks
- unit and integration tests
- launch-pack fixture validation
- Sprint 2 e2e acceptance test
- Docker Compose config check when Docker is available

## Acceptance test

```bash
python scripts/sprint2_e2e.py
```

Acceptance idea:

```text
Create a coffee lovers product brand for India.
```

Expected output includes a persisted structured Research Report with:

- trend analysis
- competitor analysis
- customer analysis
- product research
- overall score
- recommendation
- risks
- next actions

## CLI usage

Submit an idea and execute the research workflow:

```bash
python -m apps.cli.main submit "Create a coffee lovers product brand for India."
```

Retrieve a stored report:

```bash
python -m apps.cli.main report <project_id>
```

Use a temporary data directory for tests or isolated runs:

```bash
python -m apps.cli.main submit "Create a coffee lovers product brand for India." --data-dir /tmp/genesis-demo
python -m apps.cli.main report <project_id> --data-dir /tmp/genesis-demo
```

## API usage

Start API:

```bash
python -m apps.api.app
```

Health:

```bash
curl http://127.0.0.1:8000/health
```

Submit project:

```bash
curl -X POST http://127.0.0.1:8000/projects \
  -H 'Content-Type: application/json' \
  -d '{"idea":"Create a coffee lovers product brand for India."}'
```

Retrieve report:

```bash
curl http://127.0.0.1:8000/reports/<project_id>
```

## Current implementation note

EMP-001 to EMP-004 are deterministic local executables for Sprint 2. They do not call paid external APIs. This keeps Phase 1 executable in CI and locally while preserving the vertical-slice contract for future AI-backed employees.

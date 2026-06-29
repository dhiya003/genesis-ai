# Sprint 2.1.1.001 Runtime Bootstrap

Status: Implemented

## Purpose

This milestone creates the first executable Genesis AI runtime foundation for Sprint 2 while keeping Phase 1 lean and free from paid infrastructure dependencies.

## Runtime components

- `apps/api`: minimal HTTP API process with `GET /health`.
- `apps/worker`: worker bootstrap with a health payload and queue name.
- `apps/cli`: command-line entrypoint with `health` command.
- `config`: shared runtime configuration and JSON logging bootstrap.
- `tests`: standard-library regression tests for the runtime bootstrap.

## Local commands

```bash
python -m unittest discover -s tests -v
python -m apps.cli.main health
python -m apps.api.app
python -m apps.worker.main
```

The API health endpoint returns a JSON payload at:

```text
GET http://127.0.0.1:8000/health
```

## Configuration

Runtime settings are read from environment variables and have safe local defaults:

- `GENESIS_APP_NAME`
- `GENESIS_ENV`
- `GENESIS_LOG_LEVEL`
- `GENESIS_API_HOST`
- `GENESIS_API_PORT`
- `GENESIS_WORKER_QUEUE`

No real secrets are required for Sprint 2.1.1.001.

## Acceptance checklist

- API, worker, and CLI entrypoints exist.
- Runtime configuration loads from environment variables with safe defaults.
- Invalid API ports fail fast.
- Health checks produce stable JSON payloads.
- CI runs the Sprint 1 verification suite plus runtime bootstrap unit tests.

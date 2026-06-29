"""Minimal Genesis AI API runtime with a health endpoint."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from config import RuntimeConfig, configure_logging, load_runtime_config


class GenesisApiHandler(BaseHTTPRequestHandler):
    """HTTP handler for Sprint 2 runtime bootstrap endpoints."""

    server_version = "GenesisAI/0.1"

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        config: RuntimeConfig = self.server.runtime_config  # type: ignore[attr-defined]
        if self.path == "/health":
            self._send_json(200, config.health_payload("api"))
            return
        self._send_json(404, {"status": "not_found", "path": self.path})

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        logger = getattr(self.server, "runtime_logger", None)
        if logger:
            logger.info(format, *args)


def create_server(config: RuntimeConfig | None = None) -> ThreadingHTTPServer:
    runtime_config = config or load_runtime_config()
    logger = configure_logging(runtime_config.log_level)
    server = ThreadingHTTPServer((runtime_config.api_host, runtime_config.api_port), GenesisApiHandler)
    server.runtime_config = runtime_config  # type: ignore[attr-defined]
    server.runtime_logger = logger  # type: ignore[attr-defined]
    return server


def main() -> int:
    config = load_runtime_config()
    logger = configure_logging(config.log_level)
    server = create_server(config)
    logger.info("Genesis API starting on %s", config.base_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Genesis API shutdown requested")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

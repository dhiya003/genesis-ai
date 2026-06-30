"""Google Drive upload integration.

The client intentionally accepts an OAuth access token, not a client secret.
Client secrets belong in the OAuth consent/token exchange layer and should never
be persisted or echoed by Genesis.
"""

from __future__ import annotations

import json
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import request
from uuid import uuid4

DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"


@dataclass(frozen=True)
class GoogleDriveConfig:
    access_token: str
    folder_id: str | None = None
    timeout_seconds: int = 60


def google_drive_config_from_env() -> GoogleDriveConfig:
    access_token = os.getenv("GOOGLE_DRIVE_ACCESS_TOKEN", "").strip()
    if not access_token:
        raise ValueError("GOOGLE_DRIVE_ACCESS_TOKEN is required for Google Drive uploads")

    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip() or None
    timeout_raw = os.getenv("GOOGLE_DRIVE_TIMEOUT_SECONDS", "60").strip()
    try:
        timeout_seconds = int(timeout_raw)
    except ValueError as exc:
        raise ValueError("GOOGLE_DRIVE_TIMEOUT_SECONDS must be an integer") from exc
    if timeout_seconds <= 0:
        raise ValueError("GOOGLE_DRIVE_TIMEOUT_SECONDS must be greater than zero")

    return GoogleDriveConfig(access_token=access_token, folder_id=folder_id, timeout_seconds=timeout_seconds)


@dataclass
class GoogleDriveClient:
    config: GoogleDriveConfig

    def upload_file(self, path: Path, *, name: str | None = None, mime_type: str | None = None) -> dict[str, Any]:
        upload_path = Path(path)
        if not upload_path.exists() or not upload_path.is_file():
            raise ValueError(f"Upload file not found: {upload_path}")

        upload_name = name or upload_path.name
        inferred_mime_type = mime_type or mimetypes.guess_type(upload_name)[0] or "application/octet-stream"
        file_bytes = upload_path.read_bytes()
        metadata: dict[str, Any] = {"name": upload_name}
        if self.config.folder_id:
            metadata["parents"] = [self.config.folder_id]

        body, content_type = _multipart_body(metadata=metadata, file_bytes=file_bytes, mime_type=inferred_mime_type)
        url = f"{DRIVE_UPLOAD_URL}?uploadType=multipart&fields=id,name,mimeType,webViewLink"
        upload_request = request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": content_type,
            },
        )

        with request.urlopen(upload_request, timeout=self.config.timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))

        return {
            "provider": "google_drive",
            "id": response_payload.get("id"),
            "name": response_payload.get("name", upload_name),
            "mime_type": response_payload.get("mimeType", inferred_mime_type),
            "web_view_link": response_payload.get("webViewLink"),
        }


def _multipart_body(*, metadata: dict[str, Any], file_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    boundary = f"genesis-drive-{uuid4().hex}"
    metadata_bytes = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    chunks = [
        f"--{boundary}\r\n".encode("utf-8"),
        b"Content-Type: application/json; charset=UTF-8\r\n\r\n",
        metadata_bytes,
        b"\r\n",
        f"--{boundary}\r\n".encode("utf-8"),
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(chunks), f"multipart/related; boundary={boundary}"


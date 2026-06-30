from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from apps.integrations.google_drive import GoogleDriveClient, GoogleDriveConfig, google_drive_config_from_env


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class GoogleDriveIntegrationTests(unittest.TestCase):
    def test_env_config_requires_access_token(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "GOOGLE_DRIVE_ACCESS_TOKEN"):
                google_drive_config_from_env()

    def test_env_config_reads_upload_settings(self) -> None:
        with patch.dict(
            os.environ,
            {
                "GOOGLE_DRIVE_ACCESS_TOKEN": "test-token",
                "GOOGLE_DRIVE_FOLDER_ID": "folder-123",
                "GOOGLE_DRIVE_TIMEOUT_SECONDS": "15",
            },
            clear=True,
        ):
            config = google_drive_config_from_env()

        self.assertEqual(config.access_token, "test-token")
        self.assertEqual(config.folder_id, "folder-123")
        self.assertEqual(config.timeout_seconds, 15)

    def test_upload_file_posts_multipart_payload(self) -> None:
        captured: dict[str, object] = {}

        def fake_urlopen(upload_request: object, timeout: int) -> _FakeResponse:
            captured["url"] = upload_request.full_url
            captured["authorization"] = upload_request.get_header("Authorization")
            captured["content_type"] = upload_request.get_header("Content-type")
            captured["body"] = upload_request.data
            captured["timeout"] = timeout
            return _FakeResponse(
                {
                    "id": "file-123",
                    "name": "uploaded.png",
                    "mimeType": "image/png",
                    "webViewLink": "https://drive.google.com/file/d/file-123/view",
                }
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            asset_path = Path(tmpdir) / "asset.png"
            asset_path.write_bytes(b"genesis-image-bytes")
            client = GoogleDriveClient(GoogleDriveConfig(access_token="test-token", folder_id="folder-123", timeout_seconds=9))

            with patch("apps.integrations.google_drive.request.urlopen", side_effect=fake_urlopen):
                result = client.upload_file(asset_path, name="uploaded.png", mime_type="image/png")

        self.assertIn("uploadType=multipart", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer test-token")
        self.assertEqual(captured["timeout"], 9)
        self.assertIn("multipart/related", captured["content_type"])
        body = captured["body"]
        self.assertIsInstance(body, bytes)
        self.assertIn(b'"name":"uploaded.png"', body)
        self.assertIn(b'"parents":["folder-123"]', body)
        self.assertIn(b"genesis-image-bytes", body)
        self.assertEqual(result["id"], "file-123")
        self.assertEqual(result["web_view_link"], "https://drive.google.com/file/d/file-123/view")


if __name__ == "__main__":
    unittest.main()
